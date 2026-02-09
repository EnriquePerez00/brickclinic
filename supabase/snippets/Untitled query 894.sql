alter table public.early_access_responses 
add column if not exists question_3 text,
add column if not exists otherSeries text,
add column if not exists estimationType text,
add column if not exists weightValue numeric;