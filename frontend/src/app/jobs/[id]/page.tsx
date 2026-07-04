"use client";

import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import { CandidateCard } from "@/components/CandidateCard";

export default function JobDashboardPage() {
  const params = useParams();
  const jobId = params.id as string;

  const [job, setJob] = useState<any>(null);
  const [candidates, setCandidates] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    fetchJobDetails();
  }, [jobId]);

  const fetchJobDetails = async () => {
    try {
      // Temporarily mock JWT token, Auth will be implemented next
      const token = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
      
      const res = await fetch(`http://localhost:8000/jobs/`, {
        headers: { "Authorization": `Bearer ${token}` }
      });
      if (!res.ok) throw new Error("Failed to fetch jobs");
      const jobs = await res.json();
      const currentJob = jobs.find((j: any) => j.id === jobId);
      if (currentJob) setJob(currentJob);

      // Now fetch match results
      const resultsRes = await fetch(`http://localhost:8000/resumes/${jobId}/results`, {
        headers: { "Authorization": `Bearer ${token}` }
      });
      if (resultsRes.ok) {
        const results = await resultsRes.json();
        setCandidates(results);
      }
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0) return;
    setUploading(true);
    
    try {
      const token = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
      
      // Upload each file
      for (let i = 0; i < e.target.files.length; i++) {
        const file = e.target.files[i];
        const formData = new FormData();
        formData.append("file", file);
        formData.append("job_id", jobId);

        const res = await fetch(`http://localhost:8000/resumes/upload`, {
          method: "POST",
          headers: { "Authorization": `Bearer ${token}` },
          body: formData,
        });
        
        if (!res.ok) {
          console.error(`Failed to upload ${file.name}`);
        }
      }
      
      // Refresh candidates
      await fetchJobDetails();
    } catch (error) {
      console.error(error);
      alert("Error uploading files");
    } finally {
      setUploading(false);
      // Reset input
      e.target.value = '';
    }
  };

  if (loading) return <div className="p-12 text-center text-muted-foreground">Loading job details...</div>;
  if (!job) return <div className="p-12 text-center text-accent font-semibold">Job not found.</div>;

  return (
    <main className="max-w-6xl mx-auto px-6 py-12">
      <header className="mb-12">
        <h1 className="text-4xl font-serif text-primary mb-2">{job.title}</h1>
        <div className="flex gap-4 text-sm text-muted-foreground font-sans">
          <span className="px-3 py-1 bg-secondary rounded-full border border-border">
            Req Exp: {job.experience_years} years
          </span>
          <span className="px-3 py-1 bg-secondary rounded-full border border-border">
            Edu: {job.education_level}
          </span>
          <span className="px-3 py-1 bg-secondary rounded-full border border-border">
            Skills: {job.skills.join(", ")}
          </span>
        </div>
      </header>

      <section className="bg-white p-8 rounded-sm shadow-sm border border-border mb-12">
        <h2 className="text-2xl font-serif mb-4">Grade New Candidates</h2>
        <p className="text-foreground/80 mb-6 font-sans">
          Upload PDF or DOCX resumes here. Our AI will automatically parse the resumes, grade them against your rubric, and rank them below.
        </p>
        
        <label className="block w-full border-2 border-dashed border-border rounded-sm p-12 text-center cursor-pointer hover:bg-secondary/50 transition-colors">
          <span className="font-semibold text-primary block mb-2">
            {uploading ? "Uploading & Grading..." : "Click or drag resumes to upload (PDF, DOCX)"}
          </span>
          <input 
            type="file" 
            multiple 
            accept=".pdf,.docx" 
            className="hidden" 
            onChange={handleFileUpload}
            disabled={uploading}
          />
        </label>
      </section>

      <section>
        <h2 className="text-3xl font-serif mb-6 border-b border-border pb-2">Ranked Candidates ({candidates.length})</h2>
        
        {candidates.length === 0 ? (
          <div className="text-center py-12 text-muted-foreground italic border border-dashed border-border rounded-sm">
            No candidates graded yet. Upload resumes above to see rankings.
          </div>
        ) : (
          <div className="space-y-6">
            {candidates.map((c, index) => {
              // c is the MatchResult object joining with the Resume
              return (
                <CandidateCard 
                  key={c.id}
                  rank={index + 1}
                  candidateName={c.resume.candidate_name || "Unknown Candidate"}
                  totalScore={Math.round(c.total_score)}
                  semanticScore={Math.round(c.semantic_score)}
                  skillsScore={Math.round(c.skills_score)}
                  experienceScore={Math.round(c.experience_score)}
                  educationScore={Math.round(c.education_score)}
                  explanation={c.explanation}
                />
              );
            })}
          </div>
        )}
      </section>
    </main>
  );
}
