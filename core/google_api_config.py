"""
Google Cloud API Configuration
Integrates Google Cloud Natural Language API, Search Console API, and Knowledge Graph API.
"""

import os
import json
from typing import Dict, List, Optional
import traceback

# Google Cloud Natural Language API
try:
    from google.cloud import language_v1
    from google.oauth2 import service_account
    LANGUAGE_API_AVAILABLE = True
except ImportError:
    print("Google Cloud Language API not installed. Run: pip install google-cloud-language")
    LANGUAGE_API_AVAILABLE = False

# Google Search Console API
try:
    from googleapiclient.discovery import build
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    import pickle
    GSC_API_AVAILABLE = True
except ImportError:
    print("Google API Client not installed. Run: pip install google-api-python-client")
    GSC_API_AVAILABLE = False

# Knowledge Graph Search API
try:
    import requests
    KG_API_AVAILABLE = True
except ImportError:
    print("Requests library not installed. Run: pip install requests")
    KG_API_AVAILABLE = False


class GoogleCloudAPIManager:
    """Manage Google Cloud API integrations."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize API manager.

        Args:
            config_path: Path to configuration file (JSON with API keys/credentials)
        """
        self.config_path = config_path or os.path.join(os.path.dirname(__file__), '..', 'api_config.json')
        self.config = self._load_config()

        # Initialize clients
        self.language_client = None
        self.gsc_service = None

        # API keys
        self.kg_api_key = self.config.get('knowledge_graph_api_key')

    def _load_config(self) -> Dict:
        """Load API configuration from file."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading config: {e}")
                return {}
        return {}

    def setup_language_api(self, credentials_path: str) -> bool:
        """
        Setup Google Cloud Natural Language API.

        Args:
            credentials_path: Path to service account JSON file

        Returns:
            True if successful
        """
        if not LANGUAGE_API_AVAILABLE:
            print("Google Cloud Language API not available")
            return False

        try:
            credentials = service_account.Credentials.from_service_account_file(
                credentials_path
            )
            self.language_client = language_v1.LanguageServiceClient(credentials=credentials)
            print("✓ Google Cloud Natural Language API configured")
            return True
        except Exception as e:
            print(f"Error setting up Language API: {e}")
            traceback.print_exc()
            return False

    def extract_entities_from_text(self, text: str) -> Dict:
        """
        Extract entities using Google Cloud Natural Language API.

        Args:
            text: Text to analyze

        Returns:
            Entity extraction results
        """
        if not self.language_client:
            return {'error': 'Language API not configured'}

        try:
            document = language_v1.Document(
                content=text,
                type_=language_v1.Document.Type.PLAIN_TEXT
            )

            # Analyze entities
            response = self.language_client.analyze_entities(
                request={'document': document}
            )

            entities = []
            for entity in response.entities:
                entities.append({
                    'name': entity.name,
                    'type': language_v1.Entity.Type(entity.type_).name,
                    'salience': entity.salience,
                    'mentions': [
                        {
                            'text': mention.text.content,
                            'type': language_v1.EntityMention.Type(mention.type_).name
                        }
                        for mention in entity.mentions
                    ],
                    'metadata': dict(entity.metadata) if entity.metadata else {}
                })

            # Sort by salience (importance)
            entities.sort(key=lambda x: x['salience'], reverse=True)

            return {
                'entities': entities,
                'language': response.language
            }

        except Exception as e:
            print(f"Error extracting entities: {e}")
            traceback.print_exc()
            return {'error': str(e)}

    def setup_search_console(self, credentials_path: str = 'token.pickle') -> bool:
        """
        Setup Google Search Console API.

        Args:
            credentials_path: Path to OAuth credentials or token

        Returns:
            True if successful
        """
        if not GSC_API_AVAILABLE:
            print("Google Search Console API not available")
            return False

        SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly']

        try:
            creds = None

            # Load saved credentials
            if os.path.exists(credentials_path):
                with open(credentials_path, 'rb') as token:
                    creds = pickle.load(token)

            # If no valid credentials, authenticate
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    # Need OAuth flow (requires client_secret.json)
                    if not os.path.exists('client_secret.json'):
                        print("Error: client_secret.json not found. Download from Google Cloud Console.")
                        return False

                    flow = InstalledAppFlow.from_client_secrets_file(
                        'client_secret.json',
                        SCOPES
                    )
                    creds = flow.run_local_server(port=0)

                # Save credentials
                with open(credentials_path, 'wb') as token:
                    pickle.dump(creds, token)

            # Build service
            self.gsc_service = build('searchconsole', 'v1', credentials=creds)
            print("✓ Google Search Console API configured")
            return True

        except Exception as e:
            print(f"Error setting up Search Console API: {e}")
            traceback.print_exc()
            return False

    def get_search_console_queries(self,
                                   site_url: str,
                                   start_date: str,
                                   end_date: str,
                                   row_limit: int = 1000) -> Dict:
        """
        Fetch queries from Google Search Console.

        Args:
            site_url: Website URL (e.g., 'https://www.example.com/')
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            row_limit: Maximum rows to fetch

        Returns:
            Query data with clicks, impressions, CTR, position
        """
        if not self.gsc_service:
            return {'error': 'Search Console API not configured'}

        try:
            request = {
                'startDate': start_date,
                'endDate': end_date,
                'dimensions': ['query'],
                'rowLimit': row_limit
            }

            response = self.gsc_service.searchanalytics().query(
                siteUrl=site_url,
                body=request
            ).execute()

            queries = []
            for row in response.get('rows', []):
                queries.append({
                    'query': row['keys'][0],
                    'clicks': row['clicks'],
                    'impressions': row['impressions'],
                    'ctr': row['ctr'],
                    'position': row['position']
                })

            return {
                'queries': queries,
                'total_queries': len(queries)
            }

        except Exception as e:
            print(f"Error fetching Search Console data: {e}")
            traceback.print_exc()
            return {'error': str(e)}

    def search_knowledge_graph(self, query: str, limit: int = 10) -> Dict:
        """
        Search Google Knowledge Graph.

        Args:
            query: Search query (entity name)
            limit: Maximum results

        Returns:
            Knowledge Graph entities
        """
        if not KG_API_AVAILABLE:
            return {'error': 'Requests library not available'}

        if not self.kg_api_key:
            return {'error': 'Knowledge Graph API key not configured'}

        try:
            url = 'https://kgsearch.googleapis.com/v1/entities:search'

            params = {
                'query': query,
                'limit': limit,
                'key': self.kg_api_key,
                'indent': True
            }

            response = requests.get(url, params=params)
            response.raise_for_status()

            data = response.json()

            entities = []
            for element in data.get('itemListElement', []):
                result = element.get('result', {})
                entities.append({
                    'name': result.get('name'),
                    'type': result.get('@type'),
                    'description': result.get('description'),
                    'detailed_description': result.get('detailedDescription', {}).get('articleBody'),
                    'url': result.get('detailedDescription', {}).get('url'),
                    'image_url': result.get('image', {}).get('contentUrl'),
                    'result_score': element.get('resultScore')
                })

            return {
                'entities': entities,
                'total_results': len(entities)
            }

        except Exception as e:
            print(f"Error searching Knowledge Graph: {e}")
            traceback.print_exc()
            return {'error': str(e)}

    def export_config_template(self, output_path: str = 'api_config_template.json'):
        """Export a configuration template for users to fill in."""
        template = {
            "_comment": "Google Cloud API Configuration Template",
            "_instructions": {
                "knowledge_graph_api_key": "Get from Google Cloud Console > APIs & Services > Credentials",
                "natural_language_credentials": "Path to service account JSON file",
                "search_console_credentials": "Will be created via OAuth flow on first run"
            },
            "knowledge_graph_api_key": "YOUR_API_KEY_HERE",
            "natural_language_credentials_path": "path/to/service-account.json",
            "search_console_token_path": "token.pickle"
        }

        with open(output_path, 'w') as f:
            json.dump(template, f, indent=2)

        print(f"✓ Configuration template exported to: {output_path}")
        print("Fill in your API credentials and rename to 'api_config.json'")


def setup_google_apis(language_credentials: Optional[str] = None,
                     kg_api_key: Optional[str] = None) -> GoogleCloudAPIManager:
    """
    Quick setup for Google APIs.

    Args:
        language_credentials: Path to Natural Language API credentials
        kg_api_key: Knowledge Graph API key

    Returns:
        Configured API manager
    """
    manager = GoogleCloudAPIManager()

    if language_credentials:
        manager.setup_language_api(language_credentials)

    if kg_api_key:
        manager.kg_api_key = kg_api_key

    return manager


# Example usage
if __name__ == '__main__':
    # Export configuration template
    manager = GoogleCloudAPIManager()
    manager.export_config_template()

    print("\n" + "="*50)
    print("Google Cloud API Configuration Template Created!")
    print("="*50)
    print("\nNext steps:")
    print("1. Rename 'api_config_template.json' to 'api_config.json'")
    print("2. Fill in your API credentials:")
    print("   - Knowledge Graph API key")
    print("   - Natural Language API service account JSON path")
    print("3. For Search Console: Run authentication flow on first use")
    print("\nAPI Setup Instructions:")
    print("- Natural Language API: https://cloud.google.com/natural-language/docs/setup")
    print("- Search Console API: https://developers.google.com/webmaster-tools/search-console-api-original/v3/quickstart/quickstart-python")
    print("- Knowledge Graph API: https://developers.google.com/knowledge-graph")
