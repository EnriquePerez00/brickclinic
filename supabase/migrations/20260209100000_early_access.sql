create table if not exists public.early_access_responses (
  id uuid default gen_random_uuid() primary key,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null,
  question_1 text,
  question_2 text,
  email text,
  
  constraint email_check check (email ~* '^[A-Za-z0-9._+%-]+@[A-Za-z0-9.-]+[.][A-Za-z]+$')
);

alter table public.early_access_responses enable row level security;

create policy "Enable insert for all users"
on public.early_access_responses
for insert
to anon
with check (true);

create policy "Enable read for authenticated users only"
on public.early_access_responses
for select
to authenticated
using (true);
