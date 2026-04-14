import requests
import sys
import json
from datetime import datetime

class MorganaAPITester:
    def __init__(self, base_url="https://mobile-screener-hub.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
        
        result = {
            "test": name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status} - {name}")
        if details:
            print(f"   Details: {details}")

    def test_api_root(self):
        """Test API root endpoint"""
        try:
            response = requests.get(f"{self.api_url}/", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                data = response.json()
                details += f", Response: {data}"
            self.log_test("API Root Endpoint", success, details)
            return success
        except Exception as e:
            self.log_test("API Root Endpoint", False, f"Error: {str(e)}")
            return False

    def test_get_favorites_empty(self):
        """Test GET /api/favorites (should return empty list initially)"""
        try:
            response = requests.get(f"{self.api_url}/favorites", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                data = response.json()
                details += f", Count: {len(data)} favorites"
            self.log_test("GET Favorites (Initial)", success, details)
            return success, response.json() if success else []
        except Exception as e:
            self.log_test("GET Favorites (Initial)", False, f"Error: {str(e)}")
            return False, []

    def test_create_favorite(self, caceria_id="c1", caceria_name="Growth Compounders"):
        """Test POST /api/favorites"""
        try:
            payload = {
                "caceria_id": caceria_id,
                "caceria_name": caceria_name
            }
            response = requests.post(f"{self.api_url}/favorites", json=payload, timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                data = response.json()
                details += f", Created favorite: {data.get('caceria_name')}"
                return success, data
            self.log_test("POST Create Favorite", success, details)
            return success, None
        except Exception as e:
            self.log_test("POST Create Favorite", False, f"Error: {str(e)}")
            return False, None

    def test_get_favorites_with_data(self):
        """Test GET /api/favorites after creating one"""
        try:
            response = requests.get(f"{self.api_url}/favorites", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                data = response.json()
                details += f", Count: {len(data)} favorites"
                if len(data) > 0:
                    details += f", First: {data[0].get('caceria_name')}"
            self.log_test("GET Favorites (With Data)", success, details)
            return success, response.json() if success else []
        except Exception as e:
            self.log_test("GET Favorites (With Data)", False, f"Error: {str(e)}")
            return False, []

    def test_delete_favorite(self, caceria_id="c1"):
        """Test DELETE /api/favorites/{caceria_id}"""
        try:
            response = requests.delete(f"{self.api_url}/favorites/{caceria_id}", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                data = response.json()
                details += f", Message: {data.get('message')}"
            self.log_test("DELETE Favorite", success, details)
            return success
        except Exception as e:
            self.log_test("DELETE Favorite", False, f"Error: {str(e)}")
            return False

    def test_delete_nonexistent_favorite(self):
        """Test DELETE /api/favorites/{nonexistent_id} (should return 404)"""
        try:
            response = requests.delete(f"{self.api_url}/favorites/nonexistent", timeout=10)
            success = response.status_code == 404
            details = f"Status: {response.status_code} (Expected 404)"
            self.log_test("DELETE Nonexistent Favorite", success, details)
            return success
        except Exception as e:
            self.log_test("DELETE Nonexistent Favorite", False, f"Error: {str(e)}")
            return False

    def test_create_duplicate_favorite(self):
        """Test creating duplicate favorite (should return existing)"""
        try:
            # Create first favorite
            payload = {"caceria_id": "c2", "caceria_name": "Value Profundo"}
            response1 = requests.post(f"{self.api_url}/favorites", json=payload, timeout=10)
            
            # Try to create same favorite again
            response2 = requests.post(f"{self.api_url}/favorites", json=payload, timeout=10)
            
            success = response1.status_code == 200 and response2.status_code == 200
            details = f"First: {response1.status_code}, Second: {response2.status_code}"
            
            if success:
                data1 = response1.json()
                data2 = response2.json()
                details += f", Same ID: {data1.get('id') == data2.get('id')}"
            
            self.log_test("Create Duplicate Favorite", success, details)
            return success
        except Exception as e:
            self.log_test("Create Duplicate Favorite", False, f"Error: {str(e)}")
            return False

    def test_status_endpoints(self):
        """Test status check endpoints"""
        try:
            # Test POST status
            payload = {"client_name": "test_client"}
            response = requests.post(f"{self.api_url}/status", json=payload, timeout=10)
            success = response.status_code == 200
            details = f"POST Status: {response.status_code}"
            
            if success:
                # Test GET status
                response2 = requests.get(f"{self.api_url}/status", timeout=10)
                success = success and response2.status_code == 200
                details += f", GET Status: {response2.status_code}"
                if success:
                    data = response2.json()
                    details += f", Count: {len(data)} status checks"
            
            self.log_test("Status Endpoints", success, details)
            return success
        except Exception as e:
            self.log_test("Status Endpoints", False, f"Error: {str(e)}")
            return False

    def run_all_tests(self):
        """Run comprehensive API test suite"""
        print("🚀 Starting MORGANA API Tests...")
        print(f"Testing against: {self.api_url}")
        print("-" * 50)

        # Test API availability
        if not self.test_api_root():
            print("❌ API is not accessible. Stopping tests.")
            return False

        # Test favorites CRUD flow
        print("\n📋 Testing Favorites CRUD...")
        
        # Get initial state
        success, initial_favorites = self.test_get_favorites_empty()
        
        # Create a favorite
        success, created_fav = self.test_create_favorite()
        
        # Get favorites with data
        success, favorites_with_data = self.test_get_favorites_with_data()
        
        # Test duplicate creation
        self.test_create_duplicate_favorite()
        
        # Delete the favorite
        self.test_delete_favorite("c1")
        
        # Test deleting nonexistent
        self.test_delete_nonexistent_favorite()
        
        # Clean up c2 if it exists
        self.test_delete_favorite("c2")

        # Test status endpoints
        print("\n📊 Testing Status Endpoints...")
        self.test_status_endpoints()

        # Print summary
        print("\n" + "=" * 50)
        print(f"📊 Test Summary: {self.tests_passed}/{self.tests_run} tests passed")
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        print(f"✨ Success Rate: {success_rate:.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed! Backend API is working correctly.")
            return True
        else:
            print("⚠️  Some tests failed. Check the details above.")
            return False

def main():
    tester = MorganaAPITester()
    success = tester.run_all_tests()
    
    # Save detailed results
    with open('/app/backend_test_results.json', 'w') as f:
        json.dump({
            "summary": {
                "total_tests": tester.tests_run,
                "passed_tests": tester.tests_passed,
                "success_rate": (tester.tests_passed / tester.tests_run * 100) if tester.tests_run > 0 else 0,
                "timestamp": datetime.now().isoformat()
            },
            "test_results": tester.test_results
        }, f, indent=2)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())