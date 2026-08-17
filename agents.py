"""
Evolvia Africa - Multi-Agent System
Each agent has a clear responsibility and logs every important action.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
import database as db


class BaseAgent:
    name: str = "BaseAgent"

    def log(self, action: str, details: str = None, related_id: int = None):
        db.log_agent_action(self.name, action, details, related_id)


class WhatsAppAgent(BaseAgent):
    """
    Frontline agent that handles incoming messages from Principals.
    In production this would be connected to WhatsApp Business API webhooks.
    """
    name = "WhatsApp Agent"

    def handle_incoming_message(self, phone: str, message: str) -> str:
        """
        Process a message from a principal.
        Returns the reply that should be sent back via WhatsApp.
        """
        school = db.get_school_by_phone(phone)
        msg = message.strip().lower()

        # New lead
        if not school:
            self.log("New lead detected", f"Phone: {phone} | Message: {message}")
            return (
                "Hello! 👋 Welcome to *Evolvia Africa*.\n\n"
                "I am the Evolvia AI Assistant.\n\n"
                "To get started, please reply with:\n"
                "1. School Name\n"
                "2. Your Full Name (Principal)\n"
                "3. Approximate number of students\n"
                "4. School Location (County / Town)\n\n"
                "Example:\n"
                "Green Valley Academy, John Kamau, 450, Nairobi"
            )

        # Existing school – route by intent
        if any(w in msg for w in ["demo", "book", "presentation", "training", "schedule"]):
            return self._handle_booking_request(school, message)

        if any(w in msg for w in ["pay", "payment", "fee", "invoice", "mpesa"]):
            return self._handle_payment_inquiry(school)

        if any(w in msg for w in ["feedback", "how was", "rating", "review"]):
            return self._handle_feedback(school)

        if any(w in msg for w in ["status", "update", "progress"]):
            return self._handle_status(school)

        # Default
        self.log("General inquiry", f"School ID {school['id']}: {message}", school["id"])
        return (
            f"Hello {school['principal_name']} from *{school['name']}*.\n\n"
            "How can I help you today?\n\n"
            "You can ask me about:\n"
            "• Booking a demo / training\n"
            "• Payment & fees\n"
            "• Training status\n"
            "• Giving feedback"
        )

    def register_new_school(self, phone: str, name: str, principal: str, students: int, location: str) -> str:
        school_id = db.create_school(name, principal, phone, students, location)
        fee = db.calculate_monthly_fee(students)
        self.log("School registered", f"{name} | {students} students | Fee: {fee}", school_id)

        return (
            f"✅ *Registration successful!*\n\n"
            f"School: *{name}*\n"
            f"Principal: {principal}\n"
            f"Students: {students}\n"
            f"Location: {location}\n"
            f"Monthly Fee: *KES {fee:,}*\n\n"
            "Would you like to book a *Demo Presentation & Training*?\n"
            "Reply with your preferred date (e.g. 25 August 2026)"
        )

    def _handle_booking_request(self, school: Dict, message: str) -> str:
        self.log("Booking interest", message, school["id"])
        return (
            f"Great choice, {school['principal_name']}!\n\n"
            "Please reply with your preferred *date* for the Demo & Training.\n"
            "Format: DD Month YYYY (example: 22 August 2026)\n\n"
            "Our Trainer Manager AI will automatically assign a qualified trainer."
        )

    def book_demo(self, school_id: int, demo_date: str, location: str = None) -> str:
        booking_id = db.create_booking(school_id, demo_date=demo_date, location=location)
        db.update_school_status(school_id, "demo_booked")
        self.log("Demo booked", f"Date: {demo_date}", booking_id)

        # Trigger Trainer Manager
        manager = TrainerManagerAgent()
        assignment_msg = manager.auto_assign_trainer(booking_id)

        return (
            f"✅ *Demo & Training booked!*\n\n"
            f"Date: *{demo_date}*\n"
            f"Booking ID: #{booking_id}\n\n"
            f"{assignment_msg}\n\n"
            "You will receive a confirmation once the trainer is fully assigned."
        )

    def _handle_payment_inquiry(self, school: Dict) -> str:
        fee = school.get("monthly_fee") or db.calculate_monthly_fee(school["student_count"])
        return (
            f"📊 *Payment Information*\n\n"
            f"School: {school['name']}\n"
            f"Students: {school['student_count']}\n"
            f"Monthly Fee: *KES {fee:,}*\n\n"
            "After successful training we will send you the official payment details "
            "for the first term.\n\n"
            "Payment methods: M-Pesa Paybill / Bank Transfer (details provided later)."
        )

    def _handle_feedback(self, school: Dict) -> str:
        return (
            "Thank you for wanting to share feedback!\n\n"
            "Please rate the training from 1–5 and add any comments.\n"
            "Example: 5 - Excellent, trainers were very professional"
        )

    def _handle_status(self, school: Dict) -> str:
        return (
            f"Current status for *{school['name']}*:\n"
            f"• Status: {school['status'].replace('_', ' ').title()}\n"
            f"• Students: {school['student_count']}\n"
            f"• Monthly Fee: KES {school['monthly_fee']:,}"
        )


class TrainerManagerAgent(BaseAgent):
    """
    Manages real human trainers.
    Automatically assigns them and calculates their pay.
    """
    name = "Trainer Manager"

    def auto_assign_trainer(self, booking_id: int) -> str:
        booking = db.get_booking(booking_id)
        if not booking:
            return "❌ Booking not found."

        trainers = db.list_trainers(active_only=True)
        if not trainers:
            self.log("No trainers available", f"Booking #{booking_id}", booking_id)
            return (
                "⚠️ No active trainers currently registered.\n"
                "Please register trainers in the Admin panel first."
            )

        # Simple round-robin / least busy assignment
        # In production you would add location matching, availability calendar, etc.
        trainer = min(trainers, key=lambda t: t["trainings_completed"])
        db.assign_trainer(booking_id, trainer["id"])

        self.log(
            "Trainer assigned",
            f"{trainer['name']} → Booking #{booking_id} ({booking.get('school_name')})",
            booking_id
        )

        return (
            f"👤 *Trainer Assigned*\n"
            f"Name: *{trainer['name']}*\n"
            f"Phone: {trainer['phone']}\n"
            f"The trainer has been notified."
        )

    def complete_training_and_pay(self, booking_id: int, include_transport: bool = True) -> Dict:
        booking = db.get_booking(booking_id)
        if not booking or not booking.get("assigned_trainer_id"):
            return {"success": False, "message": "Booking or trainer not found"}

        db.complete_training(booking_id)
        db.update_school_status(booking["school_id"], "training_done")

        # Create payout
        payout_id = db.create_trainer_payout(
            trainer_id=booking["assigned_trainer_id"],
            booking_id=booking_id,
            transport=include_transport
        )
        payout = db.list_payouts()  # will get latest, better to fetch by id later

        self.log(
            "Training completed + payout created",
            f"Booking #{booking_id} | Payout #{payout_id}",
            booking_id
        )

        # Alert Accountant
        accountant = AccountantAgent()
        accountant.notify_new_payout(payout_id)

        return {
            "success": True,
            "message": f"Training marked complete. Payout #{payout_id} created and sent to Accountant.",
            "payout_id": payout_id
        }


class AccountantAgent(BaseAgent):
    """
    Handles all money matters: school fees + trainer payouts.
    """
    name = "Accountant"

    def create_school_invoice(self, school_id: int, period: str = "First Term") -> str:
        school = db.get_school(school_id)
        if not school:
            return "School not found"

        amount = school["monthly_fee"] or db.calculate_monthly_fee(school["student_count"])
        # For first term we can charge 3 months as example, or keep monthly
        payment_id = db.create_payment(school_id, amount, period)

        self.log("Invoice created", f"School {school['name']} | KES {amount} | {period}", payment_id)

        return (
            f"📄 *Invoice Generated*\n\n"
            f"School: {school['name']}\n"
            f"Period: {period}\n"
            f"Amount: *KES {amount:,}*\n"
            f"Invoice ID: #{payment_id}\n\n"
            "Payment Methods:\n"
            "• M-Pesa Paybill: (to be configured)\n"
            "• Bank Transfer: (to be configured)\n\n"
            "Please reply with the transaction code once paid."
        )

    def notify_new_payout(self, payout_id: int):
        self.log("New trainer payout received", f"Payout #{payout_id}", payout_id)
        # In real system this would send WhatsApp/Email to Admin + Accountant dashboard alert
        return f"Payout #{payout_id} is pending approval."

    def approve_and_pay_trainer(self, payout_id: int) -> str:
        db.approve_payout(payout_id)
        # In production: trigger actual M-Pesa B2C or bank transfer here
        db.mark_payout_paid(payout_id)

        # Update trainer earnings
        # (simplified – in real code fetch the payout first)
        self.log("Trainer payout paid", f"Payout #{payout_id}", payout_id)
        return f"✅ Payout #{payout_id} marked as paid."


class HRAgent(BaseAgent):
    name = "HR Agent"

    def register_trainer(self, name: str, phone: str, email: str = None, location: str = None) -> str:
        trainer_id = db.create_trainer(name, phone, email, location)
        self.log("New trainer onboarded", f"{name} | {phone}", trainer_id)
        return f"✅ Trainer *{name}* registered successfully (ID: {trainer_id})"

    def list_active_trainers(self) -> List[Dict]:
        return db.list_trainers(active_only=True)


class DataAnalystAgent(BaseAgent):
    name = "Data Analyst"

    def generate_admin_report(self) -> Dict[str, Any]:
        stats = db.get_dashboard_stats()
        recent_logs = db.get_recent_logs(20)

        self.log("Admin report generated", f"Schools: {stats['total_schools']} | Revenue: {stats['total_revenue']}")

        return {
            "stats": stats,
            "recent_activity": recent_logs,
            "generated_at": datetime.now().isoformat()
        }


# Convenience instances
whatsapp_agent = WhatsAppAgent()
trainer_manager = TrainerManagerAgent()
accountant = AccountantAgent()
hr_agent = HRAgent()
data_analyst = DataAnalystAgent()
