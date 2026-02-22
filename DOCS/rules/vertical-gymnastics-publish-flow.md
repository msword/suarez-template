# Gymnastics Vertical — Publish Flow

1. User calls POST /site/publish
2. API validates:
   - Org exists
   - Admin role
   - No active publish lock
3. API writes publish lock
4. API publishes Pub/Sub message:
   site_publish\_\_{env}
5. Worker:
   - Pulls Firestore snapshot
   - Generates Hugo content
   - Runs hugo build
   - Deploys to Firebase Hosting
   - Writes publish receipt
   - Clears lock
6. API returns:
   {
   "status": "queued",
   "job_id": string
   }
