-- SmartFind database setup
-- DEMO ONLY: these policies permit anonymous visitors with the public/anon key
-- to read, add, and update records. Do not use these policies for a production app.
-- Do not store sensitive personal information in this demo database.

create table if not exists public.items (
    id bigint generated always as identity primary key,
    item_name text not null,
    category text not null,
    description text,
    location text,
    item_date date,
    report_type text not null check (report_type in ('Lost', 'Found')),
    status text not null default 'Open' check (status in ('Open', 'Returned')),
    created_at timestamptz not null default now()
);

alter table public.items enable row level security;

drop policy if exists "SmartFind demo read items" on public.items;
drop policy if exists "SmartFind demo insert items" on public.items;
drop policy if exists "SmartFind demo update items" on public.items;

create policy "SmartFind demo read items"
on public.items for select
to anon, authenticated
using (true);

create policy "SmartFind demo insert items"
on public.items for insert
to anon, authenticated
with check (true);

create policy "SmartFind demo update items"
on public.items for update
to anon, authenticated
using (true)
with check (true);

grant select, insert, update on public.items to anon, authenticated;
grant usage, select on sequence public.items_id_seq to anon, authenticated;
