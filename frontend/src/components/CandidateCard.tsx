import React from 'react';
import { MatchBar } from './MatchBar';

interface CandidateCardProps {
  rank: number;
  candidateName: string;
  totalScore: number;
  semanticScore: number;
  skillsScore: number;
  experienceScore: number;
  educationScore: number;
  explanation: {
    matched_skills: string[];
    missing_skills: string[];
    experience_status: string;
    education_status: string;
    summary: string;
  };
}

export function CandidateCard({
  rank,
  candidateName,
  totalScore,
  semanticScore,
  skillsScore,
  experienceScore,
  educationScore,
  explanation
}: CandidateCardProps) {
  
  // Grade annotation logic
  let grade = "A+";
  let gradeColor = "text-success";
  if (totalScore < 90) { grade = "A"; gradeColor = "text-success"; }
  if (totalScore < 80) { grade = "B"; gradeColor = "text-primary"; }
  if (totalScore < 70) { grade = "C"; gradeColor = "text-warning"; }
  if (totalScore < 50) { grade = "F"; gradeColor = "text-accent"; }

  return (
    <div className="bg-card text-card-foreground p-6 rounded-sm shadow-sm border border-border relative mt-6 transition-all hover:shadow-md">
      
      {/* Absolute Grade Annotation */}
      <div className={`absolute -top-5 -right-3 annotation text-3xl font-bold ${gradeColor}`}>
        {grade}
      </div>
      
      <div className="flex items-center gap-4 border-b border-border pb-4 mb-5">
        <div className="w-10 h-10 rounded-full bg-secondary flex items-center justify-center font-serif text-xl font-bold">
          #{rank}
        </div>
        <div>
          <h3 className="font-serif text-2xl m-0">{candidateName}</h3>
          <p className="text-muted-foreground text-sm font-sans mt-1">
            Total Match Score: <span className="monospace-score font-bold text-primary">{totalScore}%</span>
          </p>
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Left Col: Scores */}
        <div>
          <MatchBar label="Semantic Fit" score={semanticScore} colorClass="bg-primary" maxPoints={100} />
          <MatchBar label="Skills Match" score={skillsScore} colorClass="bg-success" maxPoints={100} />
          <MatchBar label="Experience Match" score={experienceScore} colorClass="bg-accent" maxPoints={100} />
          <MatchBar label="Education Match" score={educationScore} colorClass="bg-warning" maxPoints={100} />
        </div>
        
        {/* Right Col: Details */}
        <div className="font-sans text-sm space-y-4">
          <div>
            <h4 className="font-semibold text-primary mb-2">AI Summary</h4>
            <p className="text-foreground/80 leading-relaxed italic border-l-2 border-muted pl-3">
              {explanation.summary}
            </p>
          </div>
          
          <div>
            <h4 className="font-semibold text-primary mb-2">Skills Match</h4>
            <div className="flex flex-wrap gap-2">
              {explanation.matched_skills.map(s => (
                <span key={s} className="px-2 py-1 bg-success/10 text-success border border-success/20 rounded-sm text-xs font-medium">
                  {s}
                </span>
              ))}
              {explanation.missing_skills.map(s => (
                <span key={s} className="px-2 py-1 bg-accent/10 text-accent border border-accent/20 border-dashed rounded-sm text-xs font-medium">
                  Missing: {s}
                </span>
              ))}
              {explanation.matched_skills.length === 0 && explanation.missing_skills.length === 0 && (
                <span className="text-muted-foreground italic">No specific skills analyzed.</span>
              )}
            </div>
          </div>
          
          <div>
            <h4 className="font-semibold text-primary mb-1">Experience & Education</h4>
            <ul className="list-disc list-inside text-foreground/80 space-y-1">
              <li>{explanation.experience_status}</li>
              <li>{explanation.education_status}</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
