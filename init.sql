-- Initialize databases for the Q&A system
DO $$ BEGIN
   IF NOT EXISTS (
       SELECT FROM pg_database WHERE datname = 'qa_auth'
   ) THEN
       PERFORM dblink_exec('dbname=' || current_database(), 'CREATE DATABASE qa_auth');
   END IF;
END $$;

-- Note: dblink may not be available by default; create qa_auth externally if needed.


