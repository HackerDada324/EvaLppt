import json
import time
import random
from typing import Dict, Any, List, Optional
import google.generativeai as genai
import nltk
from nltk.tokenize import sent_tokenize

class ContentAnalyzer:
    def __init__(self, api_key=None, model="gemini-2.0-flash"):
        """Initialize the content analyzer with API key and model selection."""
        self.api_key = api_key
        if not self.api_key:
            raise ValueError("API key not provided. Set GEMINI_API_KEY environment variable or pass api_key parameter.")
        
        # Configure the genai library with the API key
        genai.configure(api_key=self.api_key)
        
        self.model = model
        self.client = genai.GenerativeModel(model_name=self.model, generation_config={"temperature": 0.0})
        
        # Download NLTK resources for sentence tokenization if not already downloaded
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
        
        # Define content quality dimensions
        self.quality_dimensions = [
            "clarity",
            "coherence",
            "engagement",
            "relevance",
            "depth",
            "accuracy",
            "tone",
            "conciseness",
            "readability"
        ]
    
    def split_text_into_chunks(self, text: str, max_chunk_size: int = 1000) -> List[str]:
        """Split text into manageable chunks for API processing."""
        # First split into sentences
        sentences = sent_tokenize(text)
        
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            # If adding this sentence would exceed max_chunk_size, start a new chunk
            if len(current_chunk) + len(sentence) > max_chunk_size and current_chunk:
                chunks.append(current_chunk)
                current_chunk = sentence
            else:
                current_chunk += (" " + sentence if current_chunk else sentence)
        
        # Add the last chunk if not empty
        if current_chunk:
            chunks.append(current_chunk)
            
        return chunks
    
    def create_content_analysis_prompt(self, text: str) -> str:
        """Create a prompt for analyzing content in the desired format."""
        prompt = f"""
        Your task is to analyze the quality of the following text passage across multiple dimensions. 
        Dont Need to think about headings , just think about the quality of the content.
        
        Quality dimensions to evaluate:
        - clarity: How clear and understandable is the writing?
        - coherence: How well does the content flow logically and stay organized?
        - engagement: How captivating and interesting is the content?
        - relevance: How well does the content stay on topic and provide value?
        - depth: How substantive is the content? Does it provide meaningful insights?
        - accuracy: How factually accurate is the content?
        - tone: Is the emotional tone consistent and appropriate?
        - conciseness: How efficiently does the content express its ideas?
        - readability: How easy is the content to read and comprehend?
        
        Return your analysis as a JSON object exactly in this format:
        
        {{
          "presentationAnalysis": {{
            "contentQualityMetrics": {{
              "clarity": {{
                "score": [score between 1.0-10.0],
                "description": "How clear and understandable the content is",
                "positive feedback": "[specific feedback about clarity and why such score was given]",
                "negative feedback": "[specific feedback about clarity and why such score was given]"
              }},
              "coherence": {{
                "score": [score between 1.0-10.0],
                "description": "How well the content flows logically from one point to another",
                "positive feedback": "[specific feedback about coherence and why such score was given]",
                "negative feedback": "[specific feedback about coherence and why such score was given]"
              }},
              [repeat for all 9 dimensions]
            }},
            "overallScore": [average of all dimension scores, to 2 decimal places],
            "summaryFeedback": "[1-2 sentence overall assessment]",
            "recommendedActions": [
              "[specific action to improve the content]",
              "[specific action to improve the content]",
              "[specific action to improve the content]",
              "[specific action to improve the content]"
            ]
          }}
        }}
        
        Content to analyze: "{text}"
        
        JSON response only:
        """
        return prompt
    
    def analyze_with_retry(self, prompt: str, max_retries=5, initial_retry_delay=2, max_retry_delay=60) -> Dict[str, Any]:
        """Send prompt to Gemini API with exponential backoff for rate limits."""
        retry_delay = initial_retry_delay
        
        for attempt in range(max_retries):
            try:
                response = self.client.generate_content(prompt)
                
                # Extract JSON from response, handling markdown code blocks
                response_text = response.text
                
                # Check if response is wrapped in markdown code blocks
                if response_text.startswith("```") and "```" in response_text[3:]:
                    # Extract content between markdown code blocks
                    start_idx = response_text.find("\n") + 1
                    end_idx = response_text.rfind("```")
                    response_text = response_text[start_idx:end_idx].strip()
                
                # Remove "json" if it appears at the start of the code block
                if response_text.startswith("json"):
                    response_text = response_text[4:].strip()
                
                try:
                    result = json.loads(response_text)
                    return result
                except json.JSONDecodeError as e:
                    if attempt == max_retries - 1:
                        raise ValueError(f"Failed to parse JSON from response: {response_text}\nError: {str(e)}")
            
            except Exception as e:
                error_str = str(e).lower()
                
                # Check if error is related to rate limiting
                is_rate_limit = any(phrase in error_str for phrase in ["rate limit", "quota", "too many requests", "429"])
                
                if attempt == max_retries - 1:
                    raise
                
                # Apply exponential backoff with jitter for rate limits
                if is_rate_limit:
                    # Add jitter to prevent all retries happening simultaneously
                    jitter = random.uniform(0.5, 1.5)
                    wait_time = min(retry_delay * jitter, max_retry_delay)
                    print(f"Rate limit hit. Attempt {attempt+1} failed: {str(e)}. Waiting for {wait_time:.2f} seconds...")
                    time.sleep(wait_time)
                    # Exponential backoff
                    retry_delay *= 2
                else:
                    # For other errors, use standard retry
                    print(f"Attempt {attempt+1} failed: {str(e)}. Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    
        # If we've made it here, all retries failed
        raise Exception(f"Failed to analyze text after {max_retries} attempts")
    
    def analyze_content(self, text: str) -> Dict[str, Any]:
        """
        Perform content analysis and return in the desired JSON format.
        
        Args:
            text: Content to analyze
            
        Returns:
            Dictionary with analysis results in the presentationAnalysis format
        """
        chunks = self.split_text_into_chunks(text)
        
        # If multiple chunks, analyze each and combine results
        if len(chunks) > 1:
            all_results = []
            for i, chunk in enumerate(chunks):
                print(f"Analyzing chunk {i+1}/{len(chunks)}...")
                try:
                    prompt = self.create_content_analysis_prompt(chunk)
                    result = self.analyze_with_retry(prompt)
                    all_results.append(result)
                    # Sleep between chunks to avoid rate limits
                    if i < len(chunks) - 1:
                        time.sleep(2)
                except Exception as e:
                    print(f"Error analyzing chunk {i+1}: {str(e)}")
            
            # Combine results from all chunks
            return self._combine_analysis_results(all_results)
        else:
            # Single chunk, analyze directly
            prompt = self.create_content_analysis_prompt(text)
            return self.analyze_with_retry(prompt)
    
    def _combine_analysis_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Combine analysis results from multiple chunks."""
        if not results:
            return {}
        
        combined = {
            "presentationAnalysis": {
                "contentQualityMetrics": {},
                "overallScore": 0,
                "summaryFeedback": "",
                "recommendedActions": []
            }
        }
        
        # Process quality metrics by taking the average score across chunks
        for dimension in self.quality_dimensions:
            scores = []
            descriptions = []
            positive_feedbacks = []
            negative_feedbacks = []
            
            for result in results:
                metrics = result.get("presentationAnalysis", {}).get("contentQualityMetrics", {})
                if dimension in metrics:
                    dim_data = metrics[dimension]
                    scores.append(dim_data.get("score", 0))
                    descriptions.append(dim_data.get("description", ""))
                    positive_feedbacks.append(dim_data.get("positive feedback", ""))
                    negative_feedbacks.append(dim_data.get("negative feedback", ""))
            
            if scores:
                combined["presentationAnalysis"]["contentQualityMetrics"][dimension] = {
                    "score": round(sum(scores) / len(scores), 1),
                    "description": max(descriptions, key=len),  # Use longest description
                    "positive feedback": max(positive_feedbacks, key=len),  # Use longest positive feedback
                    "negative feedback": max(negative_feedbacks, key=len)   # Use longest negative feedback
                }
        
        # Calculate overall score as average of dimension scores
        metrics = combined["presentationAnalysis"]["contentQualityMetrics"]
        if metrics:
            dimension_scores = [dim_data["score"] for dim_data in metrics.values()]
            combined["presentationAnalysis"]["overallScore"] = round(sum(dimension_scores) / len(dimension_scores), 2)
        
        # Combine recommended actions and select most frequent
        action_counts = {}
        for result in results:
            actions = result.get("presentationAnalysis", {}).get("recommendedActions", [])
            for action in actions:
                action_counts[action] = action_counts.get(action, 0) + 1
        
        # Select top 4 recommended actions
        combined["presentationAnalysis"]["recommendedActions"] = [
            a for a, _ in sorted(action_counts.items(), key=lambda x: x[1], reverse=True)[:4]
        ]
        
        # Use the most comprehensive summary feedback
        summaries = [result.get("presentationAnalysis", {}).get("summaryFeedback", "") for result in results]
        combined["presentationAnalysis"]["summaryFeedback"] = max(summaries, key=len)
        
        return combined
    
    def print_analysis(self, analysis: Dict[str, Any]):
        """Print the analysis results in a well-formatted way."""
        try:
            pa = analysis.get("presentationAnalysis", {})
            metrics = pa.get("contentQualityMetrics", {})
            
            print("\n===== CONTENT QUALITY ANALYSIS =====")
            print(f"Overall Score: {pa.get('overallScore', 0):.2f}/10.00")
            
            print("\n----- DIMENSION SCORES -----")
            for dimension, data in metrics.items():
                print(f"{dimension.capitalize().ljust(12)}: {data.get('score', 0):.1f}/10.0")
                print(f"  {data.get('description', '')}")
                print(f"  Positive: {data.get('positive feedback', '')}")
                print(f"  Negative: {data.get('negative feedback', '')}")
                print()
            
            print("\n----- SUMMARY FEEDBACK -----")
            print(pa.get("summaryFeedback", "No summary available."))
            
            print("\n----- RECOMMENDED ACTIONS -----")
            for i, action in enumerate(pa.get("recommendedActions", []), 1):
                print(f"{i}. {action}")
            
        except Exception as e:
            print(f"Error printing analysis: {str(e)}")
            print("Raw analysis data:", json.dumps(analysis, indent=2))