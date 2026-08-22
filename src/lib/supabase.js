import { createClient } from '@supabase/supabase-js';

import {
    PUBLIC_SUPABASE_URL,
    PUBLIC_SUPABASE_PUBLISHABLE_KEY
} from '$env/static/public';

const supabaseUrl = PUBLIC_SUPABASE_URL || 'https://yofjzpycehyvrbrwyiri.supabase.co';
const supabaseKey = PUBLIC_SUPABASE_PUBLISHABLE_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlvZmp6cHljZWh5dnJicnd5aXJpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODY5ODQ4MDEsImV4cCI6MjEwMjU2MDgwMX0.uXfmWgoBhwyXpwrievxIM8haXz4eHkUxCLoBDpV3hik';

export const supabase = createClient(supabaseUrl, supabaseKey);


