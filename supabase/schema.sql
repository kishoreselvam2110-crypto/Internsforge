-- 1. Enable PGVector Extension
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Create Job Descriptions Table
CREATE TABLE public.job_descriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    skills TEXT[] NOT NULL DEFAULT '{}',
    experience_years NUMERIC(4, 2) NOT NULL DEFAULT 0.0,
    education_level TEXT,
    embedding vector(768),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 3. Create Resumes Table
CREATE TABLE public.resumes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    job_description_id UUID NOT NULL REFERENCES public.job_descriptions(id) ON DELETE CASCADE,
    file_name TEXT NOT NULL,
    file_path TEXT NOT NULL,
    raw_text TEXT NOT NULL,
    candidate_name TEXT,
    candidate_email TEXT,
    candidate_phone TEXT,
    skills TEXT[] NOT NULL DEFAULT '{}',
    experience_years NUMERIC(4, 2) NOT NULL DEFAULT 0.0,
    education_level TEXT,
    job_title TEXT,
    embedding vector(768),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 4. Create Match Results Table
CREATE TABLE public.match_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    job_description_id UUID REFERENCES public.job_descriptions(id) ON DELETE CASCADE,
    resume_id UUID REFERENCES public.resumes(id) ON DELETE CASCADE,
    total_score NUMERIC(5, 2) NOT NULL,
    semantic_score NUMERIC(5, 2) NOT NULL,
    skills_score NUMERIC(5, 2) NOT NULL,
    experience_score NUMERIC(5, 2) NOT NULL,
    education_score NUMERIC(5, 2) NOT NULL,
    explanation JSONB NOT NULL, -- matched_skills, missing_skills, experience_gap, summary text
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    CONSTRAINT unique_job_resume UNIQUE (job_description_id, resume_id)
);

-- 5. Indexes for Vector Search
CREATE INDEX ON public.job_descriptions USING hnsw (embedding vector_cosine_ops);
CREATE INDEX ON public.resumes USING hnsw (embedding vector_cosine_ops);

-- 6. Enable Row Level Security (RLS)
ALTER TABLE public.job_descriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.resumes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.match_results ENABLE ROW LEVEL SECURITY;

-- 7. RLS Policies
-- Job Descriptions Policies
CREATE POLICY "Allow users to read their own job descriptions" 
    ON public.job_descriptions FOR SELECT TO authenticated USING (auth.uid() = user_id);
CREATE POLICY "Allow users to insert their own job descriptions" 
    ON public.job_descriptions FOR INSERT TO authenticated WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Allow users to update their own job descriptions" 
    ON public.job_descriptions FOR UPDATE TO authenticated USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Allow users to delete their own job descriptions" 
    ON public.job_descriptions FOR DELETE TO authenticated USING (auth.uid() = user_id);

-- Resumes Policies
CREATE POLICY "Allow users to read their own resumes" 
    ON public.resumes FOR SELECT TO authenticated USING (auth.uid() = user_id);
CREATE POLICY "Allow users to insert their own resumes" 
    ON public.resumes FOR INSERT TO authenticated WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Allow users to delete their own resumes" 
    ON public.resumes FOR DELETE TO authenticated USING (auth.uid() = user_id);

-- Match Results Policies
CREATE POLICY "Allow users to read their own match results" 
    ON public.match_results FOR SELECT TO authenticated USING (auth.uid() = user_id);
CREATE POLICY "Allow users to insert their own match results" 
    ON public.match_results FOR INSERT TO authenticated WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Allow users to delete their own match results" 
    ON public.match_results FOR DELETE TO authenticated USING (auth.uid() = user_id);

-- 8. Create Storage Bucket for Resumes
-- Supabase Storage buckets are represented in the storage.buckets table.
INSERT INTO storage.buckets (id, name, public) 
VALUES ('resumes', 'resumes', false) 
ON CONFLICT (id) DO NOTHING;

-- RLS Policies for Storage.objects
-- Resume files will be uploaded at path: {user_id}/{job_id}/{filename}
CREATE POLICY "Allow authenticated users to read resumes from storage" 
    ON storage.objects FOR SELECT TO authenticated USING (bucket_id = 'resumes' AND auth.uid()::text = (storage.foldername(name))[1]);
CREATE POLICY "Allow authenticated users to upload resumes to storage" 
    ON storage.objects FOR INSERT TO authenticated WITH CHECK (bucket_id = 'resumes' AND auth.uid()::text = (storage.foldername(name))[1]);
CREATE POLICY "Allow authenticated users to delete resumes from storage" 
    ON storage.objects FOR DELETE TO authenticated USING (bucket_id = 'resumes' AND auth.uid()::text = (storage.foldername(name))[1]);
