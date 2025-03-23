import os
import json
import time
import random
import re
from typing import Dict, Any, List
import google.generativeai as genai
import nltk
from nltk.tokenize import sent_tokenize
nltk.download('punkt_tab')

class DisfluencyTagger:
    def __init__(self, api_key=None, model="gemini-2.0-flash"):
        """Initialize the tagger with API key and model selection."""
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
        
        # Define disfluency types for prompt engineering
        self.disfluency_types = [
            "FILLER",      # um, uh, like, you know
            "REP",         # repetitions (I I I think)
            "RESTART",     # false starts/self-corrections
            "ABANDON",     # abandoned sentences
            "INTERJ",      # interjections/parenthetical comments
            "LENGTHEN",    # lengthened sounds (sooooo)
            "SWAP",        # word swaps/mid-sentence changes
            "GRAM",        # grammatical errors
            "STUTTER",     # stuttering
            "INCOMPLETE"   # incomplete sentences
        ]
    
    def create_prompt(self, text: str) -> str:
        """Create a prompt for the Gemini model."""
        prompt = f"""
        Your task is to identify and tag disfluencies in the following text. 
        Use BIO tagging format:
        - B-[TYPE]: Beginning of a disfluency of type [TYPE]
        - I-[TYPE]: Inside (continuation) of a disfluency of type [TYPE]
        - O: Regular speech (no disfluency)
        
        Disfluency types:
        - FILLER: Filled pauses like "um", "uh", "like", "you know"
        - REP: Repetitions where words or phrases are repeated unintentionally
        - RESTART: False starts or self-corrections where the speaker changes direction
        - ABANDON: Sentence abandonment where thought is not completed
        - INTERJ: Interjections or parenthetical comments
        - LENGTHEN: Lengthened sounds or drawn-out speech
        - SWAP: Mid-sentence word swaps or changes
        - GRAM: Unintended grammatical errors
        - STUTTER: Stuttering where syllables or sounds are involuntarily repeated
        - INCOMPLETE: Incomplete sentences
        
        Example:
        Text: "I was, um, thinking that we could, uh, maybe go to the the store later."
        Expected JSON:
        {{
          "tokens": ["I", "was", ",", "um", ",", "thinking", "that", "we", "could", ",", "uh", ",", "maybe", "go", "to", "the", "the", "store", "later", "."],
          "tags": ["O", "O", "O", "B-FILLER", "O", "O", "O", "O", "O", "O", "B-FILLER", "O", "O", "O", "O", "B-REP", "I-REP", "O", "O", "O"],
          "explanation": "Tagged 'um' and 'uh' as fillers, and the repeated word 'the' as a repetition disfluency."
        }}
        
        Return your analysis as a JSON object with these fields:
        1. "tokens": array of all words/tokens
        2. "tags": array of corresponding BIO tags
        3. "explanation": brief explanation of your tagging decisions
        
        Text to analyze: "{text}"
        
        JSON response only:
        """
        return prompt

    def split_text_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences using NLTK."""
        return sent_tokenize(text)

    def tag_text(self, text: str, max_retries=5, initial_retry_delay=2, max_retry_delay=60) -> Dict[str, Any]:
        """Tag disfluencies in the text using Gemini with exponential backoff for rate limits."""
        prompt = self.create_prompt(text)
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
                    # Validate response structure
                    if not all(k in result for k in ["tokens", "tags", "explanation"]):
                        raise ValueError("Missing required fields in response")
                    if len(result["tokens"]) != len(result["tags"]):
                        raise ValueError("Token and tag counts don't match")
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
        raise Exception(f"Failed to tag text after {max_retries} attempts")
    
    def tag_passage(self, passage: str, batch_size=1) -> List[Dict[str, Any]]:
        """
        Tag an entire passage by splitting it into sentences and processing each one.
        Optionally processes sentences in batches to control API usage.
        
        Args:
            passage: A text passage to analyze
            batch_size: Number of sentences to process in each batch
            
        Returns:
            List of dictionaries with tagged results for each sentence
        """
        # Split the passage into sentences
        sentences = self.split_text_into_sentences(passage)
        results = []
        
        # Process sentences in batches
        for i in range(0, len(sentences), batch_size):
            batch = sentences[i:i+batch_size]
            
            for sentence in batch:
                # Skip empty sentences
                if not sentence.strip():
                    continue
                    
                try:
                    result = self.tag_text(sentence)
                    # Add the original sentence to the result
                    result["sentence"] = sentence
                    results.append(result)
                    print(f"Successfully tagged: {sentence}")
                except Exception as e:
                    print(f"Error tagging sentence: {sentence}")
                    print(f"Error details: {str(e)}")
                    # Add a failed result to maintain the sentence order
                    results.append({
                        "sentence": sentence,
                        "tokens": [],
                        "tags": [],
                        "explanation": f"Failed to tag: {str(e)}",
                        "error": str(e)
                    })
                    
            # Sleep between batches to avoid hitting rate limits too quickly
            if i + batch_size < len(sentences):
                time.sleep(2)  # 2-second pause between batches
                
        return results
    
    def get_disfluency_stats(self, tagged_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate statistics about disfluencies in the tagged results.
        
        Args:
            tagged_results: List of tagged sentence results
            
        Returns:
            Dictionary with disfluency statistics
        """
        stats = {
            "total_sentences": len(tagged_results),
            "total_tokens": 0,
            "sentences_with_disfluencies": 0,
            "disfluency_counts": {disfluency_type: 0 for disfluency_type in self.disfluency_types},
            "disfluency_examples": {disfluency_type: [] for disfluency_type in self.disfluency_types}
        }
        
        for result in tagged_results:
            # Skip results with errors
            if "error" in result:
                continue
                
            tokens = result.get("tokens", [])
            tags = result.get("tags", [])
            
            stats["total_tokens"] += len(tokens)
            
            # Check if sentence contains any disfluencies
            has_disfluency = any(tag != "O" for tag in tags)
            if has_disfluency:
                stats["sentences_with_disfluencies"] += 1
            
            # Count disfluencies by type and collect examples
            i = 0
            while i < len(tags):
                if tags[i].startswith("B-"):
                    # Extract the disfluency type
                    disfluency_type = tags[i][2:]  # Remove "B-" prefix
                    
                    # Count the disfluency
                    stats["disfluency_counts"][disfluency_type] += 1
                    
                    # Collect example
                    start_idx = i
                    i += 1
                    while i < len(tags) and tags[i].startswith("I-"):
                        i += 1
                    
                    # Extract the disfluency example
                    disfluency_text = " ".join(tokens[start_idx:i])
                    
                    # Get some context (up to 5 tokens before and after)
                    context_start = max(0, start_idx - 5)
                    context_end = min(len(tokens), i + 5)
                    context = " ".join(tokens[context_start:context_end])
                    
                    # Store example with context
                    if len(stats["disfluency_examples"][disfluency_type]) < 5:  # Limit to 5 examples per type
                        stats["disfluency_examples"][disfluency_type].append({
                            "text": disfluency_text,
                            "context": context
                        })
                else:
                    i += 1
        
        # Calculate percentages
        if stats["total_tokens"] > 0:
            stats["percent_with_disfluencies"] = (stats["sentences_with_disfluencies"] / stats["total_sentences"]) * 100
            
            # Calculate overall disfluency rate (disfluencies per 100 tokens)
            total_disfluencies = sum(stats["disfluency_counts"].values())
            stats["disfluencies_per_100_tokens"] = (total_disfluencies / stats["total_tokens"]) * 100
            
        return stats
    
    def analyze_passage(self, passage: str, batch_size=1) -> Dict[str, Any]:
        """
        Analyze a passage and return both tagged results and statistics without writing to files.
        
        Args:
            passage: A text passage to analyze
            batch_size: Number of sentences to process in each batch
            
        Returns:
            Dictionary with 'results' (tagged sentences) and 'stats' (disfluency statistics)
        """
        # Tag the passage
        results = self.tag_passage(passage, batch_size)
        
        # Generate statistics from the results
        stats = self.get_disfluency_stats(results)
        
        # Return both results and stats
        return {
            "results": results,
            "stats": stats
        }

    def print_disfluency_stats(self, stats: Dict[str, Any]):
        """
        Print disfluency statistics in a well-formatted way.
        
        Args:
            stats: Dictionary containing disfluency statistics
        """
        try:
            # Print summary statistics
            print("\n===== DISFLUENCY ANALYSIS SUMMARY =====")
            print(f"Total sentences analyzed: {stats['total_sentences']}")
            print(f"Total tokens processed: {stats['total_tokens']}")
            print(f"Sentences with disfluencies: {stats['sentences_with_disfluencies']} " 
                  f"({stats.get('percent_with_disfluencies', 0):.1f}%)")
            print(f"Overall disfluency rate: {stats.get('disfluencies_per_100_tokens', 0):.2f} per 100 tokens")
            
            # Print disfluency counts by type
            print("\n----- DISFLUENCY COUNTS BY TYPE -----")
            for disfluency_type, count in sorted(stats['disfluency_counts'].items(), 
                                                key=lambda x: x[1], reverse=True):
                if count > 0:
                    print(f"  {disfluency_type.ljust(10)}: {count}")
            
            # Print examples for each disfluency type
            print("\n----- DISFLUENCY EXAMPLES -----")
            for disfluency_type, examples in stats['disfluency_examples'].items():
                if examples:  # Only print types that have examples
                    print(f"\n{disfluency_type} examples:")
                    for i, example in enumerate(examples, 1):
                        print(f"  {i}. Text: \"{example['text']}\"")
                        print(f"     Context: \"{example['context']}\"")
            
        except Exception as e:
            print(f"Error while printing statistics: {str(e)}")