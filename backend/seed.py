import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SECRET_KEY")

if not url or not key:
    print("Please set SUPABASE_URL and SUPABASE_SECRET_KEY in your .env file.")
    exit(1)

client = create_client(url, key)

users = client.auth.admin.list_users()
user_map = {u.email: u.id for u in users}
print("Found Auth Users:", list(user_map.keys()))

# 1. Seed Caregivers
caregiver_emails = ["caregiver@vcare.life", "demo.caregiver@vcare.life"]
for email in caregiver_emails:
    if email in user_map:
        cg_id = user_map[email]
        client.table("profiles").upsert({
            "id": cg_id,
            "email": email,
            "full_name": "Demo Caregiver",
            "role": "caregiver",
            "phone": "+919876543210",
            "onboarding_complete": True
        }).execute()
        print(f"Caregiver profile seeded for {email} ({cg_id})")

# 2. Seed Senior
senior_id = user_map.get("senior@vcare.life")
if senior_id:
    client.table("profiles").upsert({
        "id": senior_id,
        "email": "senior@vcare.life",
        "full_name": "Kalyani Devi",
        "role": "senior",
        "phone": "+919876543211",
        "date_of_birth": "1952-04-15",
        "preferred_language": "Hindi / English",
        "emergency_contact_name": "Demo Caregiver",
        "emergency_contact_relationship": "Son",
        "emergency_contact_phone": "+919876543210",
        "onboarding_complete": True
    }).execute()
    print(f"Senior profile seeded for Kalyani Devi ({senior_id})")

    # 3. Link caregivers to this senior
    for email in caregiver_emails:
        if email in user_map:
            cg_id = user_map[email]
            client.table("caregiver_links").upsert({
                "caregiver_id": cg_id,
                "senior_id": senior_id
            }, on_conflict="caregiver_id,senior_id").execute()
            print(f"Linked {email} to senior {senior_id}")

    # 4. Medications
    meds = [
        {"senior_id": senior_id, "name": "Metformin (Blood Sugar)", "dosage": "500mg", "scheduled_time": "08:00 AM", "taken": True},
        {"senior_id": senior_id, "name": "Amlodipine (Blood Pressure)", "dosage": "5mg", "scheduled_time": "02:00 PM", "taken": False},
        {"senior_id": senior_id, "name": "Calcium + Vitamin D3", "dosage": "1 Tablet", "scheduled_time": "08:30 PM", "taken": False}
    ]
    client.table("medications").delete().eq("senior_id", senior_id).execute()
    client.table("medications").insert(meds).execute()
    print("Medications seeded")

    # 5. Call Log
    call = {
        "senior_id": senior_id,
        "call_id": "call_demo_01",
        "status": "completed",
        "transcript": "Vcare: Hello Kalyani ji! Did you take your morning Metformin? Senior: Yes beta, I took it right after breakfast. Vcare: Wonderful! Have a great day.",
        "duration": 45,
        "distress_detected": False
    }
    client.table("call_logs").delete().eq("senior_id", senior_id).execute()
    client.table("call_logs").insert(call).execute()
    print("Call log seeded")

print("\nALL SEEDING COMPLETED SUCCESSFULLY!")
