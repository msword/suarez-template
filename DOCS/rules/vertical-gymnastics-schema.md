# Gymnastics Vertical — Firestore Schema

Root Path:

orgs/{org_id}/site/

---

## hero_slides

Collection: hero_slides

Document:

{
"order": number,
"title": string,
"subtitle": string,
"image": string,
"ctaText": string,
"ctaUrl": string,
"active": boolean,
"createdAt": ISO8601,
"updatedAt": ISO8601
}

---

## navigation

Document: navigation/main

{
"items": [
{
"label": string,
"url": string,
"order": number,
"children": []
}
],
"updatedAt": ISO8601
}

---

## site_settings

Document: site_settings/config

{
"templateType": "gymnastics",
"theme": {
"primaryColor": string,
"accentColor": string,
"fontFamily": string
},
"meta": {
"title": string,
"description": string,
"keywords": []
},
"updatedAt": ISO8601
}

---

## coaches

Collection: coaches

{
"name": string,
"title": string,
"bio": string,
"image": string,
"order": number,
"active": boolean
}

---

## competitions

Collection: competitions

{
"year": number,
"name": string,
"location": string,
"startDate": ISO8601,
"endDate": ISO8601,
"slug": string
}
