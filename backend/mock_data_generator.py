"""
Mock data generator for testing without real API keys
"""
import random
from typing import List, Dict, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class MockDataGenerator:
    """Generate realistic mock data for testing"""
    
    def __init__(self):
        self.store_names = [
            "Sainsbury's London Bridge",
            "Sainsbury's Manchester Central",
            "Sainsbury's Birmingham High Street",
            "Sainsbury's Edinburgh Royal Mile",
            "Sainsbury's Bristol City Centre"
        ]
        
        self.review_templates = [
            "Great store with friendly staff. {aspect}",
            "The store is clean and well-organized. {aspect}",
            "Long queues at checkout but good selection. {aspect}",
            "Staff are helpful and the store is easy to navigate. {aspect}",
            "Some shelves were empty but overall good experience. {aspect}",
            "Excellent customer service. {aspect}",
            "Could be cleaner but staff are friendly. {aspect}",
            "Quick checkout and well-stocked shelves. {aspect}"
        ]
        
        self.aspects = [
            "The waiting time was minimal.",
            "Staff were very helpful.",
            "The store was spotless.",
            "Easy to find what I needed.",
            "Good product availability.",
            "Nice layout.",
            "Queue was a bit long.",
            "Some items were out of stock.",
            "Store could be cleaner."
        ]
    
    def generate_google_reviews(self, store_name: str, count: int = 10) -> List[Dict[str, Any]]:
        """Generate mock Google reviews matching SERP API Google Maps review format"""
        reviews = []
        
        for i in range(count):
            rating = random.choices([1, 2, 3, 4, 5], weights=[5, 10, 15, 35, 35])[0]
            aspect = random.choice(self.aspects)
            template = random.choice(self.review_templates)
            days_ago = random.randint(1, 90)
            
            # Match SERP API Google Maps review format
            review = {
                "user": {
                    "name": f"Customer {i+1}",
                    "link": f"https://www.google.com/maps/contrib/{random.randint(100000000, 999999999)}",
                    "thumbnail": f"https://lh3.googleusercontent.com/a/mock-avatar-{i}.jpg"
                },
                "rating": rating,
                "date": f"{days_ago} days ago" if days_ago > 7 else f"{days_ago} days ago",
                "snippet": template.format(aspect=aspect),
                "likes": random.randint(0, 20),
                "images": [] if random.random() > 0.3 else [
                    {
                        "thumbnail": f"https://lh5.googleusercontent.com/mock-image-{i}.jpg"
                    }
                ],
                "response": None if random.random() > 0.2 else {
                    "date": f"{days_ago - random.randint(1, 3)} days ago",
                    "snippet": "Thank you for your feedback! We appreciate your visit."
                }
            }
            reviews.append(review)
        
        return reviews
    
    def generate_sql_transactions(self, store_id: str, count: int = 100) -> List[Dict[str, Any]]:
        """Generate mock transaction data matching CustomerTransactions model"""
        products = [
            ("Fresh Milk", "Dairy", 2.50),
            ("Bread", "Bakery", 1.20),
            ("Chicken Breast", "Meat", 5.99),
            ("Apples", "Produce", 3.50),
            ("Orange Juice", "Beverages", 3.00),
            ("Pasta", "Pantry", 1.50),
            ("Cheese", "Dairy", 4.25),
            ("Tomatoes", "Produce", 2.80)
        ]
        
        genders = ["Male", "Female", "Other"]
        income_levels = ["<£20k", "£20k-£40k", "£40k-£60k", "£60k-£80k", ">£80k"]
        payment_methods = ["Credit Card", "Debit Card", "Cash", "Mobile Payment"]
        feedbacks = ["Excellent", "Good", "Average", "Poor", "Very Poor"]
        
        transactions = []
        base_date = datetime.now() - timedelta(days=30)
        
        for i in range(count):
            product, category, base_price = random.choice(products)
            total_quantity = random.randint(1, 5)
            unit_price = base_price * random.uniform(0.9, 1.1)
            transaction_date = base_date + timedelta(days=random.randint(0, 30))
            
            # Match CustomerTransactions model exactly
            transaction = {
                "transaction_id": f"TXN{store_id[-3:]}{i:04d}",
                "customer_id": f"CUST{random.randint(1000, 9999)}",
                "store_id": store_id,
                "age": random.randint(18, 75),
                "gender": random.choice(genders),
                "income": random.choice(income_levels),
                "date": transaction_date.strftime("%Y-%m-%d"),
                "year": transaction_date.year,
                "month": transaction_date.strftime("%B"),
                "day": transaction_date.day,
                "time": f"{random.randint(8, 20):02d}:{random.randint(0, 59):02d}:00",
                "total_quantity": total_quantity,
                "unit_price": round(unit_price, 2),
                "total_amount": round(unit_price * total_quantity, 2),
                "product": product,
                "product_category": category,
                "customer_feedback": random.choice(feedbacks),
                "payment_method": random.choice(payment_methods)
            }
            transactions.append(transaction)
        
        return transactions
    
    def generate_employee_data(self, store_id: str, count: int = 15) -> List[Dict[str, Any]]:
        """Generate mock employee shift data matching EmployeeShifts model"""
        roles = ["Cashier", "Stock Clerk", "Store Manager", "Customer Service Representative", "Department Supervisor"]
        names = ["John Smith", "Emma Wilson", "Michael Brown", "Sarah Davis", 
                "James Taylor", "Lisa Anderson", "David Thomas", "Mary Jackson",
                "Robert Johnson", "Jennifer Lee", "William Martinez", "Patricia Garcia"]
        months = ["January", "February", "March", "April", "May", "June", 
                 "July", "August", "September", "October", "November", "December"]
        
        employees = []
        for i in range(count):
            shift_date = datetime.now() - timedelta(days=random.randint(0, 30))
            clock_in_hour = random.randint(6, 14)
            shift_length = random.choice([4, 6, 8])
            clock_out_hour = clock_in_hour + shift_length
            
            # Match EmployeeShifts model exactly
            emp = {
                "employee_id": f"EMP{store_id[-3:]}{i:03d}",
                "employee_name": random.choice(names),
                "store_id": store_id,
                "assigned_role": random.choice(roles),
                "date": shift_date.strftime("%Y-%m-%d"),
                "month": shift_date.strftime("%B"),
                "clock_in": f"{clock_in_hour:02d}:00:00",
                "clock_out": f"{clock_out_hour:02d}:00:00",
                "shift_hours": f"{shift_length:02d}:00:00"
            }
            employees.append(emp)
        
        return employees
    
    def generate_employee_info(self, store_id: str, count: int = 10) -> List[Dict[str, Any]]:
        """Generate mock employee info matching EmployeeInfo model"""
        roles = ["Cashier", "Stock Clerk", "Store Manager", "Customer Service Representative", "Department Supervisor"]
        names = ["John Smith", "Emma Wilson", "Michael Brown", "Sarah Davis", 
                "James Taylor", "Lisa Anderson", "David Thomas", "Mary Jackson",
                "Robert Johnson", "Jennifer Lee"]
        
        employees = []
        for i in range(count):
            hire_date = datetime.now() - timedelta(days=random.randint(365, 3650))
            tenure_years = (datetime.now() - hire_date).days / 365.25
            
            # Match EmployeeInfo model exactly
            emp = {
                "employee_id": f"EMP{store_id[-3:]}{i:03d}",
                "employee_name": names[i] if i < len(names) else f"Employee {i}",
                "store_id": store_id,
                "assigned_role": random.choice(roles),
                "hire_date": hire_date.strftime("%Y-%m-%d"),
                "tenure_years": round(tenure_years, 2),
                "overall_employee_performance_rating": random.randint(1, 5)
            }
            employees.append(emp)
        
        return employees
    
    def generate_image_analysis_mock(self, image_path: str) -> Dict[str, Any]:
        """Generate mock image analysis results"""
        # Randomize scores to simulate different conditions
        cleanliness_score = random.randint(60, 95)
        empty_shelves_score = random.randint(55, 90)
        queue_score = random.randint(50, 85)
        staff_score = random.randint(60, 90)
        organization_score = random.randint(65, 95)
        
        analysis = {
            "cleanliness": {
                "score": cleanliness_score,
                "details": f"Store cleanliness rated at {cleanliness_score}/100. {'Generally clean' if cleanliness_score > 75 else 'Needs attention'}."
            },
            "empty_shelves": {
                "score": empty_shelves_score,
                "details": f"Shelf stocking at {empty_shelves_score}/100. {'Well stocked' if empty_shelves_score > 75 else 'Some gaps detected'}."
            },
            "queue_length": {
                "score": queue_score,
                "details": f"Queue management at {queue_score}/100. {'Minimal queues' if queue_score > 70 else 'Long queues observed'}."
            },
            "staff_presence": {
                "score": staff_score,
                "details": f"Staff visibility at {staff_score}/100. {'Good coverage' if staff_score > 75 else 'More staff needed'}."
            },
            "store_organization": {
                "score": organization_score,
                "details": f"Organization rated at {organization_score}/100. {'Well organized' if organization_score > 80 else 'Could be improved'}."
            },
            "immediate_issues": []
        }
        
        # Add issues if scores are low
        if cleanliness_score < 70:
            analysis["immediate_issues"].append("Cleaning required in main aisles")
        if empty_shelves_score < 65:
            analysis["immediate_issues"].append("Restock needed in multiple sections")
        if queue_score < 60:
            analysis["immediate_issues"].append("Open additional checkout lanes")
        
        return analysis
    
    def generate_embedding_mock(self, dimension: int = 1536) -> List[float]:
        """Generate mock embedding vector"""
        return [random.gauss(0, 0.1) for _ in range(dimension)]


# Global instance
mock_data_gen = MockDataGenerator()
