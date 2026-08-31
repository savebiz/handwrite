-- HandWrite Verify — Supabase Database Schema & Policy Setup Script
-- Run this script in the Supabase SQL Editor (https://app.supabase.com -> Project -> SQL Editor)

-- 1. Document Records Table
CREATE TABLE IF NOT EXISTS public.document_records (
    document_id TEXT PRIMARY KEY,
    document_type TEXT NOT NULL,
    record_status TEXT NOT NULL,
    record_data JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Audit Events Table
CREATE TABLE IF NOT EXISTS public.audit_events (
    id BIGSERIAL PRIMARY KEY,
    document_id TEXT REFERENCES public.document_records(document_id) ON DELETE CASCADE,
    actor TEXT NOT NULL,
    action TEXT NOT NULL,
    details JSONB DEFAULT '{}'::jsonb,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- Index for fast lookup on document_id and record_status
CREATE INDEX IF NOT EXISTS idx_document_records_status ON public.document_records(record_status);
CREATE INDEX IF NOT EXISTS idx_audit_events_doc_id ON public.audit_events(document_id);

-- 3. Enable Row Level Security (RLS)
ALTER TABLE public.document_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.audit_events ENABLE ROW LEVEL SECURITY;

-- 4. RLS Policies for Anon & Service Role Access (Hackathon Demo Scope)
DROP POLICY IF EXISTS "Allow public read access on document_records" ON public.document_records;
CREATE POLICY "Allow public read access on document_records"
    ON public.document_records FOR SELECT
    USING (true);

DROP POLICY IF EXISTS "Allow public write access on document_records" ON public.document_records;
CREATE POLICY "Allow public write access on document_records"
    ON public.document_records FOR ALL
    USING (true)
    WITH CHECK (true);

DROP POLICY IF EXISTS "Allow public read access on audit_events" ON public.audit_events;
CREATE POLICY "Allow public read access on audit_events"
    ON public.audit_events FOR SELECT
    USING (true);

DROP POLICY IF EXISTS "Allow public write access on audit_events" ON public.audit_events;
CREATE POLICY "Allow public write access on audit_events"
    ON public.audit_events FOR ALL
    USING (true)
    WITH CHECK (true);
