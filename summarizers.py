"""
Summarization Engines Module
Provides local (extractive) and online (AI-powered) summarization.
"""

import re
from typing import List, Optional


class LocalSummarizer:
    """
    Local extractive summarizer using TextRank algorithm.
    Works offline without any API keys.
    """
    
    def __init__(self):
        self._initialized = False
        self._nlp_ready = False
    
    def _initialize(self):
        """Initialize NLTK components on first use."""
        if self._initialized:
            return
        
        import nltk
        
        # Download required NLTK data
        required_packages = ['punkt', 'punkt_tab', 'stopwords']
        for package in required_packages:
            try:
                nltk.data.find(f'tokenizers/{package}' if 'punkt' in package else f'corpora/{package}')
            except LookupError:
                nltk.download(package, quiet=True)
        
        self._initialized = True
    
    def summarize(self, text: str, length: str = 'medium') -> str:
        """
        Generate an extractive summary using TextRank.
        
        Args:
            text: Input text to summarize
            length: 'short', 'medium', or 'long'
            
        Returns:
            Summarized text
        """
        self._initialize()
        
        from sumy.parsers.plaintext import PlaintextParser
        from sumy.nlp.tokenizers import Tokenizer
        from sumy.summarizers.text_rank import TextRankSummarizer
        from sumy.nlp.stemmers import Stemmer
        from sumy.utils import get_stop_words
        
        # Determine sentence count based on length
        sentence_counts = {
            'short': 3,
            'medium': 5,
            'long': 8
        }
        sentence_count = sentence_counts.get(length, 5)
        
        # Parse and summarize
        parser = PlaintextParser.from_string(text, Tokenizer("english"))
        stemmer = Stemmer("english")
        summarizer = TextRankSummarizer(stemmer)
        summarizer.stop_words = get_stop_words("english")
        
        sentences = summarizer(parser.document, sentence_count)
        summary = ' '.join(str(sentence) for sentence in sentences)
        
        return summary if summary else text[:500] + "..."
    
    def extract_key_points(self, text: str, max_points: int = 5) -> List[str]:
        """
        Extract key points from text.
        
        Args:
            text: Input text
            max_points: Maximum number of key points
            
        Returns:
            List of key point strings
        """
        self._initialize()
        
        from sumy.parsers.plaintext import PlaintextParser
        from sumy.nlp.tokenizers import Tokenizer
        from sumy.summarizers.lsa import LsaSummarizer
        from sumy.nlp.stemmers import Stemmer
        from sumy.utils import get_stop_words
        
        parser = PlaintextParser.from_string(text, Tokenizer("english"))
        stemmer = Stemmer("english")
        summarizer = LsaSummarizer(stemmer)
        summarizer.stop_words = get_stop_words("english")
        
        sentences = summarizer(parser.document, max_points)
        key_points = [str(sentence).strip() for sentence in sentences]
        
        return key_points if key_points else [text[:200] + "..."]


class OnlineSummarizer:
    """
    AI-powered summarizer using Google Gemini API.
    Requires an API key.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self._model = None
    
    def _get_model(self):
        """Get or create the Gemini model."""
        if self._model is None:
            if not self.api_key:
                raise ValueError("API key is required for online summarization. Get one at https://aistudio.google.com/")
            
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self._model = genai.GenerativeModel('gemini-1.5-flash')
        
        return self._model
    
    def summarize(self, text: str, length: str = 'medium') -> str:
        """
        Generate a summary using Gemini AI.
        
        Args:
            text: Input text to summarize
            length: 'short', 'medium', or 'long'
            
        Returns:
            AI-generated summary
        """
        model = self._get_model()
        
        length_instructions = {
            'short': 'in 2-3 sentences',
            'medium': 'in 4-6 sentences',
            'long': 'in a detailed paragraph of 8-10 sentences'
        }
        
        prompt = f"""Summarize the following text {length_instructions.get(length, 'in 4-6 sentences')}. 
Focus on the main ideas and key information. Be concise and clear.

TEXT:
{text[:10000]}

SUMMARY:"""
        
        response = model.generate_content(prompt)
        return response.text.strip()
    
    def extract_key_points(self, text: str, max_points: int = 5) -> List[str]:
        """
        Extract key points using AI.
        
        Args:
            text: Input text
            max_points: Maximum number of key points
            
        Returns:
            List of key point strings
        """
        model = self._get_model()
        
        prompt = f"""Extract exactly {max_points} key points from the following text.
Format each point as a clear, concise bullet point.
Return ONLY the bullet points, one per line, starting with "•".

TEXT:
{text[:10000]}

KEY POINTS:"""
        
        response = model.generate_content(prompt)
        
        # Parse bullet points
        lines = response.text.strip().split('\n')
        key_points = []
        
        for line in lines:
            line = line.strip()
            # Remove bullet point markers
            line = re.sub(r'^[•\-\*]\s*', '', line)
            if line and len(key_points) < max_points:
                key_points.append(line)
        
        return key_points if key_points else [response.text.strip()]


def get_summarizer(mode: str = 'local', api_key: Optional[str] = None):
    """
    Factory function to get a summarizer instance.
    
    Args:
        mode: 'local' or 'online'
        api_key: API key for online mode
        
    Returns:
        Summarizer instance
    """
    if mode == 'online':
        return OnlineSummarizer(api_key)
    return LocalSummarizer()
