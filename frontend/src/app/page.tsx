import Link from 'next/link';

export default function Home() {
  return (
    <main className="max-w-6xl mx-auto px-6 py-12">
      <header className="mb-16 border-b border-border pb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-5xl font-serif text-primary mb-2">Talent AI.</h1>
            <p className="text-muted-foreground font-sans text-lg">
              Intelligent Resume Screening & Grading
            </p>
          </div>
          <nav>
            {/* We will add Auth UI here later */}
            <Link 
              href="/jobs/new" 
              className="px-6 py-3 bg-primary text-primary-foreground font-medium rounded-sm shadow-sm hover:bg-primary/90 transition-colors"
            >
              Create Job &rarr;
            </Link>
          </nav>
        </div>
      </header>

      <section className="grid grid-cols-1 md:grid-cols-2 gap-12">
        <div>
          <h2 className="text-3xl font-serif mb-6">Automate the <span className="text-accent italic">first pass.</span></h2>
          <p className="text-foreground/80 text-lg leading-relaxed mb-6">
            Upload a batch of resumes, and our AI pipeline will extract skills, experience, and education to generate a detailed match score against your job description.
          </p>
          <div className="bg-white p-8 rounded-sm shadow-sm border border-border relative">
            {/* Decorative annotation */}
            <div className="absolute -top-4 -right-4 annotation text-2xl font-bold">
              92% Match!
            </div>
            
            <h3 className="font-serif text-xl mb-4 border-b border-border pb-2">Sample Grading Rubric</h3>
            
            <div className="space-y-4 font-sans text-sm">
              <div className="flex justify-between items-center">
                <span className="font-medium">Semantic Similarity (50%)</span>
                <span className="monospace-score text-success font-semibold">48/50</span>
              </div>
              <div className="w-full bg-muted h-2 rounded-full overflow-hidden">
                <div className="bg-success h-full w-[96%]"></div>
              </div>
              
              <div className="flex justify-between items-center mt-4">
                <span className="font-medium">Skills Overlap (30%)</span>
                <span className="monospace-score text-warning font-semibold">20/30</span>
              </div>
              <div className="w-full bg-muted h-2 rounded-full overflow-hidden">
                <div className="bg-warning h-full w-[66%]"></div>
              </div>
            </div>
          </div>
        </div>
        
        <div className="bg-secondary rounded-sm p-10 flex flex-col justify-center border border-border border-dashed">
          <h3 className="font-serif text-2xl mb-4 text-secondary-foreground text-center">Ready to grade?</h3>
          <p className="text-center text-muted-foreground mb-8">
            Create a job description to get started.
          </p>
          <Link 
            href="/jobs/new"
            className="mx-auto px-8 py-4 bg-primary text-primary-foreground font-medium rounded-sm hover:opacity-90 transition-opacity flex items-center gap-2"
          >
            Create Job Description &rarr;
          </Link>
        </div>
      </section>
    </main>
  );
}
