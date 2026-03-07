"""
Seed database with 2026 grants.

DEVELOPER GUIDELINE: Database Seeding & Idempotency
Adds all relevant grants for 2026 to the grant planning database. Ensure 
the seed script uses UPSERT operations (INSERT ... ON CONFLICT) to remain 
idempotent, preventing duplicate records on multiple executions.
"""

import logging

from grant_automation_cli.grant_database import GrantDatabase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def seed_2026_grants():
    """Seed database with 2026 grants."""
    db = GrantDatabase()

    grants_2026 = [
        {
            "name": "Moving Stories: Short-Form Graphic Novels for King County Metro Transit RapidRide",
            "identifier": "moving-stories-rapidride-2026",
            "deadline": "January 13, 2026",
            "status": "in_progress",
            "amount_requested": 75000,
            "organization_name": "Key Tech Labs",
            "project_title": "Green STEM Expo - Graphic Novel Series",
            "description": "Short-form graphic novels for public transit that tell engaging stories about sustainability, technology, and community. These visual narratives will be displayed in King County Metro Transit RapidRide vehicles, reaching thousands of daily commuters with educational and inspiring content.",
            "focus_areas": "Arts, Education, Public Engagement, Sustainability",
            "eligibility_requirements": "Non-profit organizations, artists, and community groups serving King County",
            "application_url": "https://apply.4culture.org/grants/moving-stories",
            "notes": "High priority grant for public engagement and arts education",
            "priority": 8,
        },
        {
            "name": "Touring Art Roster + Presenter Incentive",
            "identifier": "touring-art-roster-2026",
            "deadline": "February 15, 2026",
            "status": "planned",
            "amount_requested": 50000,
            "organization_name": "Key Tech Labs",
            "project_title": "STEM Education Touring Program",
            "description": "Touring program bringing STEM education and interactive exhibits to schools and community centers throughout King County. Includes hands-on workshops, demonstrations, and educational materials.",
            "focus_areas": "Education, Arts, Community Engagement, STEM",
            "eligibility_requirements": "Non-profit organizations with touring capabilities",
            "application_url": "https://apply.4culture.org/grants/touring-art-roster",
            "notes": "Good opportunity for expanding educational reach",
            "priority": 6,
        },
        {
            "name": "Arts Education Project Support",
            "identifier": "arts-education-project-2026",
            "deadline": "March 1, 2026",
            "status": "planned",
            "amount_requested": 40000,
            "organization_name": "Key Tech Labs",
            "project_title": "Green STEM Expo Educational Program",
            "description": "Comprehensive arts education program combining environmental science, technology, and creative expression. Includes curriculum development, teacher training, and student workshops.",
            "focus_areas": "Arts Education, STEM, Environmental Education",
            "eligibility_requirements": "Educational organizations, schools, or non-profits with education programs",
            "application_url": "https://apply.4culture.org/grants/arts-education",
            "notes": "Aligns well with existing Green STEM Expo program",
            "priority": 7,
        },
        {
            "name": "Heritage Projects",
            "identifier": "heritage-projects-2026",
            "deadline": "April 10, 2026",
            "status": "planned",
            "amount_requested": 35000,
            "organization_name": "Key Tech Labs",
            "project_title": "Community Sustainability Heritage Documentation",
            "description": "Documentation and preservation of community sustainability practices and innovations. Includes oral histories, archival work, and digital preservation of community knowledge.",
            "focus_areas": "Heritage, Community, Sustainability, Documentation",
            "eligibility_requirements": "Heritage organizations, historical societies, or community groups",
            "application_url": "https://apply.4culture.org/grants/heritage",
            "notes": "Long-term project with community impact",
            "priority": 5,
        },
        {
            "name": "Arts Facilities",
            "identifier": "arts-facilities-2026",
            "deadline": "May 5, 2026",
            "status": "planned",
            "amount_requested": 100000,
            "organization_name": "Key Tech Labs",
            "project_title": "Community Arts and STEM Center",
            "description": "Development and operation of a community center combining arts and STEM education. Includes facility improvements, equipment, and programming support.",
            "focus_areas": "Facilities, Arts, Education, Community Space",
            "eligibility_requirements": "Organizations with facilities or facility development plans",
            "application_url": "https://apply.4culture.org/grants/arts-facilities",
            "notes": "Major capital project - requires detailed planning",
            "priority": 9,
        },
        {
            "name": "Sustained Support",
            "identifier": "sustained-support-2026",
            "deadline": "June 1, 2026",
            "status": "planned",
            "amount_requested": 60000,
            "organization_name": "Key Tech Labs",
            "project_title": "Sustained Operations Support",
            "description": "Multi-year operational support for ongoing programs including Green STEM Expo, community workshops, and educational initiatives.",
            "focus_areas": "Operations, General Support, Sustainability",
            "eligibility_requirements": "Established organizations with proven track record",
            "application_url": "https://apply.4culture.org/grants/sustained-support",
            "notes": "Important for long-term sustainability",
            "priority": 8,
        },
        {
            "name": "Arts Project Support",
            "identifier": "arts-project-support-2026",
            "deadline": "July 15, 2026",
            "status": "planned",
            "amount_requested": 45000,
            "organization_name": "Key Tech Labs",
            "project_title": "Community Arts Festival",
            "description": "Annual community arts festival celebrating local artists, sustainability, and technology. Includes performances, exhibitions, workshops, and community engagement activities.",
            "focus_areas": "Arts, Community, Festivals, Public Engagement",
            "eligibility_requirements": "Non-profit organizations organizing public events",
            "application_url": "https://apply.4culture.org/grants/arts-project",
            "notes": "Annual event - good for community visibility",
            "priority": 6,
        },
        {
            "name": "Cultural Facilities",
            "identifier": "cultural-facilities-2026",
            "deadline": "August 20, 2026",
            "status": "planned",
            "amount_requested": 80000,
            "organization_name": "Key Tech Labs",
            "project_title": "Cultural and Educational Space Enhancement",
            "description": "Enhancement of cultural and educational spaces to better serve the community. Includes accessibility improvements, technology upgrades, and programming infrastructure.",
            "focus_areas": "Facilities, Accessibility, Technology, Culture",
            "eligibility_requirements": "Organizations with cultural facilities",
            "application_url": "https://apply.4culture.org/grants/cultural-facilities",
            "notes": "Infrastructure improvement project",
            "priority": 7,
        },
        {
            "name": "Arts and Heritage Collections",
            "identifier": "arts-heritage-collections-2026",
            "deadline": "September 10, 2026",
            "status": "planned",
            "amount_requested": 30000,
            "organization_name": "Key Tech Labs",
            "project_title": "Digital Archive and Collection Management",
            "description": "Development of digital archive system for preserving and sharing community arts and heritage collections. Includes digitization, cataloging, and public access platform.",
            "focus_areas": "Collections, Heritage, Digital Preservation, Archives",
            "eligibility_requirements": "Organizations with collections or archival needs",
            "application_url": "https://apply.4culture.org/grants/collections",
            "notes": "Technical project with long-term value",
            "priority": 5,
        },
        {
            "name": "Arts and Culture Capacity Building",
            "identifier": "capacity-building-2026",
            "deadline": "October 5, 2026",
            "status": "planned",
            "amount_requested": 25000,
            "organization_name": "Key Tech Labs",
            "project_title": "Organizational Development and Capacity Building",
            "description": "Support for organizational development including staff training, strategic planning, board development, and systems improvement to enhance organizational capacity.",
            "focus_areas": "Capacity Building, Organizational Development, Training",
            "eligibility_requirements": "Non-profit organizations seeking to build capacity",
            "application_url": "https://apply.4culture.org/grants/capacity-building",
            "notes": "Important for organizational growth",
            "priority": 6,
        },
        {
            "name": "Arts and Heritage Preservation",
            "identifier": "preservation-2026",
            "deadline": "November 15, 2026",
            "status": "planned",
            "amount_requested": 35000,
            "organization_name": "Key Tech Labs",
            "project_title": "Community Heritage Preservation Initiative",
            "description": "Preservation of community heritage including historic sites, artifacts, documents, and cultural practices. Includes conservation work, documentation, and public education.",
            "focus_areas": "Preservation, Heritage, Conservation, History",
            "eligibility_requirements": "Organizations involved in heritage preservation",
            "application_url": "https://apply.4culture.org/grants/preservation",
            "notes": "Long-term preservation project",
            "priority": 5,
        },
        {
            "name": "Arts and Culture Innovation",
            "identifier": "innovation-2026",
            "deadline": "December 1, 2026",
            "status": "planned",
            "amount_requested": 55000,
            "organization_name": "Key Tech Labs",
            "project_title": "Innovative Arts and Technology Integration",
            "description": "Innovative project combining arts, technology, and community engagement. Includes new media art, interactive installations, and technology-driven creative experiences.",
            "focus_areas": "Innovation, Technology, Arts, New Media",
            "eligibility_requirements": "Organizations proposing innovative projects",
            "application_url": "https://apply.4culture.org/grants/innovation",
            "notes": "Cutting-edge project with high visibility potential",
            "priority": 7,
        },
    ]

    added_count = 0
    updated_count = 0
    skipped_count = 0

    for grant_data in grants_2026:
        try:
            # Idempotent write via UPSERT in GrantDatabase
            grant_id = db.add_grant(grant_data)
            logger.info(f"✅ Upserted grant: {grant_data['name']}")
            added_count += 1

            # Add milestone for deadline
            if grant_data.get("deadline"):
                try:
                    # Parse deadline to YYYY-MM-DD format
                    deadline_parts = grant_data["deadline"].replace(",", "").split()
                    if len(deadline_parts) >= 3:
                        month_map = {
                            "January": "01",
                            "February": "02",
                            "March": "03",
                            "April": "04",
                            "May": "05",
                            "June": "06",
                            "July": "07",
                            "August": "08",
                            "September": "09",
                            "October": "10",
                            "November": "11",
                            "December": "12",
                        }
                        month = month_map.get(deadline_parts[0], "01")
                        day = deadline_parts[1].zfill(2)
                        year = deadline_parts[2]
                        deadline_iso = f"{year}-{month}-{day}"
                        db.add_milestone(
                            grant_id,
                            "Application Deadline",
                            deadline_iso,
                            "Final deadline for grant application submission",
                        )
                except RuntimeError as e:
                    logger.warning(f"Could not add milestone for grant {grant_id}: {e}")

        except RuntimeError as e:
            logger.error(f"Error adding grant {grant_data['name']}: {e}")
            skipped_count += 1

    db.close()

    print("\n✅ Database seeding complete!")
    print(f"   Processed: {added_count} grants via UPSERT")
    print(f"\n   Total grants actively managed: {added_count}")
    print("\n   Generate dashboard to view: python -m grant_automation_cli.cli dashboard")


if __name__ == "__main__":
    seed_2026_grants()
