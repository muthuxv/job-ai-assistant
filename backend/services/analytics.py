# backend/services/analytics.py
from sqlalchemy.orm import Session
from models.models import Application, Job
from datetime import datetime, timedelta
from collections import defaultdict

class Analytics:
    
    @staticmethod
    def get_dashboard_stats(db: Session) -> dict:
        """
        Statistiques pour le dashboard
        """
        total_applications = db.query(Application).count()
        
        # Par statut
        status_counts = {
            "draft": db.query(Application).filter(Application.status == "draft").count(),
            "applied": db.query(Application).filter(Application.status == "applied").count(),
            "interview": db.query(Application).filter(Application.status == "interview").count(),
            "rejected": db.query(Application).filter(Application.status == "rejected").count(),
            "offer": db.query(Application).filter(Application.status == "offer").count()
        }
        
        # Score moyen
        apps_with_score = db.query(Application).filter(
            Application.match_score.isnot(None)
        ).all()
        avg_score = (
            sum(app.match_score for app in apps_with_score) / len(apps_with_score)
            if apps_with_score else 0
        )
        
        # Taux de réponse (applied -> interview/offer)
        applied_count = status_counts["applied"]
        positive_count = status_counts["interview"] + status_counts["offer"]
        response_rate = (
            (positive_count / applied_count * 100)
            if applied_count > 0 else 0
        )
        
        # Timeline (derniers 30 jours)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_apps = db.query(Application).filter(
            Application.created_at >= thirty_days_ago
        ).all()
        
        # Grouper par semaine
        timeline = defaultdict(int)
        for app in recent_apps:
            week_start = app.created_at.date() - timedelta(days=app.created_at.weekday())
            timeline[week_start.isoformat()] += 1
        
        timeline_list = [
            {"week": week, "count": count}
            for week, count in sorted(timeline.items())
        ]
        
        # Top entreprises
        jobs_applied = db.query(Application).filter(
            Application.status.in_(["applied", "interview", "offer"])
        ).all()
        
        companies = defaultdict(int)
        for app in jobs_applied:
            job = db.query(Job).filter(Job.id == app.job_id).first()
            if job:
                companies[job.company] += 1
        
        top_companies = [
            {"company": company, "count": count}
            for company, count in sorted(companies.items(), key=lambda x: x[1], reverse=True)[:5]
        ]
        
        return {
            "total_applications": total_applications,
            "by_status": status_counts,
            "average_match_score": round(avg_score, 1),
            "response_rate": round(response_rate, 1),
            "timeline": timeline_list,
            "top_companies": top_companies
        }