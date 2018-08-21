import { Component, OnInit } from '@angular/core';
import { Router, ActivatedRoute, ParamMap } from '@angular/router';
import { Observable } from "rxjs/internal/Observable";
import { switchMap } from "rxjs/operators";

import { faComment, faMicrophoneAlt, faCodeBranch} from '@fortawesome/free-solid-svg-icons';

import { Skill, SkillsService } from "../skills.service";

@Component({
  selector: 'marketplace-skill-detail',
  templateUrl: './skill-detail.component.html',
  styleUrls: ['./skill-detail.component.scss']
})
export class SkillDetailComponent implements OnInit {
    githubIcon = faCodeBranch;
    skillIcon = faMicrophoneAlt;
    skill$: Observable<Skill>;
    triggerIcon = faComment;

    constructor(
        private route: ActivatedRoute,
        private router: Router,
        private service: SkillsService
    ) { }


    ngOnInit() {
        this.skill$ = this.route.paramMap.pipe(
            switchMap((params: ParamMap) => this.service.getSkillById(params.get('id')))
        );
    }

    navigateToGithubRepo(githubRepoUrl) {
        window.open(githubRepoUrl);
    }
    // returnToSummary() {
    //     this.router.navigate(['/skills']);
    // }
}