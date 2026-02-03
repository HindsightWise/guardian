import logging
import arxiv
from typing import List, Dict, Any

class ScholarOfficer:
    """The Scholar: Bridges Aion with the world of academic research via ArXiv.
    
    This officer provides tools for searching and retrieving metadata from 
    scientific papers, focusing on quantitative and peer-reviewed sources.
    """
    
    def __init__(self) -> None:
        """Initializes the Scholar officer and its ArXiv client."""
        self.logger = logging.getLogger("Scholar")
        self.client = arxiv.Client()

    def search_papers(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Searches the ArXiv database for scientific papers matching a query.
        
        Args:
            query: The search term or category (e.g., 'cat:q-bio').
            max_results: The maximum number of papers to retrieve.
            
        Returns:
            A list of dictionaries containing paper titles, summaries, and URLs.
        """
        self.logger.info(f"📜 Scholar: Searching ArXiv for -> '{query}'")
        
        try:
            search = arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.SubmittedDate
            )

            results: List[Dict[str, Any]] = []
            for r in self.client.results(search):
                paper = {
                    "title": str(r.title),
                    "summary": str(r.summary),
                    "authors": [a.name for a in r.authors],
                    "url": str(r.pdf_url),
                    "published": str(r.published)
                }
                results.append(paper)
                
            return results
        except Exception as e:
            self.logger.error(f"❌ Scholar: Search failed: {e}")
            return []

    def get_latest_biology(self) -> List[Dict[str, Any]]:
        """A specialized shortcut for retrieving the latest biology-related papers.
        
        Returns:
            A list of the 3 most recent papers in the quantitative biology category.
        """
        return self.search_papers("cat:q-bio", max_results=3)
