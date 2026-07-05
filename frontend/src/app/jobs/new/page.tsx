"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function CreateJobPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    title: "",
    description: "",
    skills: "",
    experience_years: 0,
    education_level: "Bachelor's",
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const payload = {
        ...formData,
        skills: formData.skills.split(",").map(s => s.trim()).filter(Boolean),
        experience_years: Number(formData.experience_years)
      };

      const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const res = await fetch(`${API}/jobs/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY}`
        },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        throw new Error(await res.text());
      }

      const job = await res.json();
      router.push(`/jobs/${job.id}`);
    } catch (error) {
      console.error(error);
      alert("Failed to create job.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="max-w-4xl mx-auto px-6 py-12">
      <div className="mb-8">
        <h1 className="text-4xl font-serif text-primary mb-2">Create Job Description</h1>
        <p className="text-muted-foreground font-sans">Define the role and grading rubric.</p>
      </div>

      <form onSubmit={handleSubmit} className="bg-white p-8 rounded-sm shadow-sm border border-border space-y-6">
        <div>
          <label className="block text-sm font-semibold mb-1">Job Title</label>
          <input
            type="text"
            required
            className="w-full border border-border rounded-sm px-3 py-2 bg-background focus:outline-none focus:border-primary"
            placeholder="e.g. Senior Software Engineer"
            value={formData.title}
            onChange={e => setFormData({ ...formData, title: e.target.value })}
          />
        </div>

        <div>
          <label className="block text-sm font-semibold mb-1">Description</label>
          <textarea
            required
            rows={5}
            className="w-full border border-border rounded-sm px-3 py-2 bg-background focus:outline-none focus:border-primary"
            placeholder="Describe the responsibilities and team..."
            value={formData.description}
            onChange={e => setFormData({ ...formData, description: e.target.value })}
          />
        </div>

        <div>
          <label className="block text-sm font-semibold mb-1">Required Skills (Comma separated)</label>
          <input
            type="text"
            className="w-full border border-border rounded-sm px-3 py-2 bg-background focus:outline-none focus:border-primary"
            placeholder="Python, React, PostgreSQL, Docker"
            value={formData.skills}
            onChange={e => setFormData({ ...formData, skills: e.target.value })}
          />
        </div>

        <div className="grid grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-semibold mb-1">Experience (Years)</label>
            <input
              type="number"
              min="0"
              step="0.5"
              required
              className="w-full border border-border rounded-sm px-3 py-2 bg-background focus:outline-none focus:border-primary"
              value={formData.experience_years}
              onChange={e => setFormData({ ...formData, experience_years: parseFloat(e.target.value) })}
            />
          </div>
          <div>
            <label className="block text-sm font-semibold mb-1">Minimum Education</label>
            <select
              className="w-full border border-border rounded-sm px-3 py-2 bg-background focus:outline-none focus:border-primary"
              value={formData.education_level}
              onChange={e => setFormData({ ...formData, education_level: e.target.value })}
            >
              <option value="High School">High School</option>
              <option value="Associate&apos;s">Associate&apos;s</option>
              <option value="Bachelor&apos;s">Bachelor&apos;s</option>
              <option value="Master&apos;s">Master&apos;s</option>
              <option value="PhD">PhD</option>
            </select>
          </div>
        </div>

        <div className="pt-6 border-t border-border flex justify-end">
          <button
            type="submit"
            disabled={loading}
            className="px-6 py-3 bg-primary text-primary-foreground font-medium rounded-sm disabled:opacity-50"
          >
            {loading ? "Creating..." : "Save & Continue"}
          </button>
        </div>
      </form>
    </main>
  );
}
