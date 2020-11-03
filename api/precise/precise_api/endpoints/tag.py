# Mycroft Server - Backend
# Copyright (C) 2020 Mycroft AI Inc
# SPDX-License-Identifier: 	AGPL-3.0-or-later
#
# This file is part of the Mycroft Server.
#
# The Mycroft Server is free software: you can redistribute it and/or
# modify it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
"""Precise API endpoint for tagging a file."""

import getpass
from http import HTTPStatus
from os import environ
from pathlib import Path
from random import choice
from typing import List

from schematics import Model
from schematics.types import StringType

from selene.api import SeleneEndpoint
from selene.data.tagging import (
    WakeWordFileTag,
    FileTagRepository,
    SessionRepository,
    Tag,
    TaggableFile,
    Tagger,
    TaggerRepository,
    TagRepository,
    WakeWordFileRepository,
)
from selene.util.ssh import get_remote_file, SshClientConfig


class TagPostRequest(Model):
    """Define the expected arguments to be passed in the POST request."""

    tag_id = StringType()
    tag_value = StringType()
    file_name = StringType()


class TagEndpoint(SeleneEndpoint):
    """Precise API endpoint for tagging a file.

    The HTTP GET request will randomly select a type of tag, which will in turn be used
    to retrieve an audio file that requires the tag.  The selected audio file must not
    have been tagged in the last hour.  This will prevent the same files from being
    tagged more times than necessary.  The file will also be copied to local storage
    for a subsequent API call.
    """

    def get(self):
        """Handle an HTTP GET request."""
        self._authenticate()
        response_data, file_to_tag = self._build_response_data()
        if response_data:
            self._copy_audio_file(file_to_tag)

        return response_data, HTTPStatus.OK if response_data else HTTPStatus.NO_CONTENT

    def _build_response_data(self):
        """Build the response from data retrieved from the database

        :return the response and the taggable file object
        """
        wake_word = self.request.args["wakeWord"].replace("-", " ")
        file_to_tag = self._get_taggable_file(wake_word)
        tag = self._get_random_tag(file_to_tag)
        if file_to_tag is None:
            response_data = ""
        else:
            response_data = dict(
                audioFileId=file_to_tag.id,
                audioFileName=file_to_tag.name,
                tagId=tag.id,
                tagInstructions=tag.instructions,
                tagName=(wake_word if tag.name == "wake word" else tag.name).title(),
                tagTitle=tag.title,
                tagValues=tag.values,
            )

        return response_data, file_to_tag

    def _get_taggable_file(self, wake_word: str) -> TaggableFile:
        """Get a file that has still requires some tagging for a specified tag type.

        :param wake_word: the wake word being tagged by the user
        :return: dataclass instance representing the file to be tagged
        """
        file_repository = WakeWordFileRepository(self.db)
        file_to_tag = file_repository.get_taggable_file(wake_word)

        return file_to_tag

    def _get_random_tag(self, file_to_tag: TaggableFile) -> Tag:
        """Get a random tag that has not yet been designated to the wake word sample.



        :param file_to_tag: Attributes of the file that will be tagged by the user.
        :return:
        """
        all_tags = self._get_all_tags()
        if None in file_to_tag.designations:
            tags = {tag.name: tag for tag in all_tags}
            random_tag = tags["wake word"]
        else:
            tags = {tag.id: tag for tag in all_tags}
            for designation in file_to_tag.designations:
                del tags[designation["tag_id"]]
            random_tag = choice(list(tags.values()))

        return random_tag

    def _get_all_tags(self) -> List[Tag]:
        """Randomly pick one of the tag types.

        :return a dataclass instance representing the tag type
        """
        tag_repository = TagRepository(self.db)
        tags = tag_repository.get_all()

        return tags

    @staticmethod
    def _copy_audio_file(file_to_tag: TaggableFile):
        """Copy the file from the location specified in the database to local storage

        :param file_to_tag: dataclass instance representing the file to be tagged
        """
        local_path = Path(environ["SELENE_DATA_DIR"]).joinpath(file_to_tag.name)
        if not local_path.exists():
            if file_to_tag.location.server == environ["PRECISE_SERVER"]:
                remote_user = "precise"
                ssh_port = environ["PRECISE_SSH_PORT"]
            else:
                remote_user = "mycroft"
                ssh_port = 22
            ssh_config = SshClientConfig(
                local_user=getpass.getuser(),
                remote_server=file_to_tag.location.server,
                remote_user=remote_user,
                ssh_port=ssh_port,
            )
            remote_path = Path(file_to_tag.location.directory).joinpath(
                file_to_tag.name
            )
            get_remote_file(ssh_config, local_path, remote_path)

    def post(self):
        """Process HTTP POST request for an account."""
        self._authenticate()
        self._validate_post_request()
        tagger = self._ensure_tagger_exists()
        session_id = self._ensure_session_exists(tagger)
        self._add_tag(session_id)

        return dict(sessionId=session_id), HTTPStatus.OK

    def _validate_post_request(self):
        """Validate the contents of the request object for a POST request."""
        post_request = TagPostRequest(
            dict(
                tag_id=self.request.json.get("tagId"),
                tag_value=self.request.json.get("tagValue"),
                file_name=self.request.json.get("audioFileId"),
            )
        )
        post_request.validate()

    def _ensure_tagger_exists(self):
        tagger = Tagger(entity_type="account", entity_id=self.account.id)
        tagger_repository = TaggerRepository(self.db)
        tagger.id = tagger_repository.ensure_tagger_exists(tagger)

        return tagger

    def _ensure_session_exists(self, tagger):
        session_repository = SessionRepository(self.db)
        session_id = session_repository.ensure_session_exists(tagger)

        return session_id

    def _add_tag(self, session_id: str):
        file_tag = WakeWordFileTag(
            file_id=self.request.json["audioFileId"],
            session_id=session_id,
            tag_id=self.request.json["tagId"],
            tag_value_id=self.request.json["tagValueId"],
        )
        file_tag_repository = FileTagRepository(self.db)
        file_tag_repository.add(file_tag)