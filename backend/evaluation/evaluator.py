"""
Comprehensive Presentation Evaluation System
Calculates overall scores and detailed feedback for presentations
"""
import json
from datetime import datetime
from typing import Dict, List, Any, Tuple
import numpy as np

class PresentationEvaluator:
    """Main evaluator that combines all analysis results into comprehensive scores"""
    
    def __init__(self):
        # Define scoring weights for different aspects
        self.weights = {
            'body_language': 0.25,      # 25% - Body posture and movement
            'vocal_delivery': 0.20,     # 20% - Speech quality and disfluency
            'content_quality': 0.30,    # 30% - Content analysis
            'facial_expression': 0.15,  # 15% - Facial expressions and engagement
            'technical_aspects': 0.10   # 10% - Video/audio technical quality
        }
        
        # Scoring criteria
        self.score_ranges = {
            'excellent': (90, 100),
            'very_good': (80, 89),
            'good': (70, 79),
            'fair': (60, 69),
            'needs_improvement': (0, 59)
        }
    
    def evaluate_body_language(self, analysis_results: Dict) -> Dict:
        """Evaluate body language based on motion analysis"""
        scores = {}
        feedback = []
        
        # Body rotation analysis
        if 'body_rotation' in analysis_results and 'error' not in analysis_results['body_rotation']:
            body_data = analysis_results['body_rotation']
            
            # Stability score (less movement = more stable)
            stability = max(0, 100 - (body_data.get('std_dev_angle', 10) * 5))
            scores['body_stability'] = min(stability, 100)
            
            # Direction variety (some movement is good)
            dir_percentages = body_data.get('direction_percentages', {})
            if dir_percentages:
                center_percentage = dir_percentages.get('center', 0)
                if center_percentage > 70:
                    scores['body_positioning'] = 85 + (center_percentage - 70) * 0.5
                    feedback.append("✓ Good central positioning")
                elif center_percentage > 50:
                    scores['body_positioning'] = 70 + (center_percentage - 50) * 0.75
                    feedback.append("→ Decent positioning, could be more centered")
                else:
                    scores['body_positioning'] = max(40, center_percentage)
                    feedback.append("⚠ Consider maintaining more central positioning")
        
        # Head motion analysis
        if 'head_motion' in analysis_results and 'error' not in analysis_results['head_motion']:
            head_data = analysis_results['head_motion']
            
            # Natural head movement (some movement is good, too much is distracting)
            head_stability = head_data.get('stability_score', 50)
            if 70 <= head_stability <= 90:
                scores['head_movement'] = 85
                feedback.append("✓ Natural head movement patterns")
            elif head_stability > 90:
                scores['head_movement'] = 70
                feedback.append("→ Consider more natural head movements")
            else:
                scores['head_movement'] = max(50, head_stability)
                feedback.append("⚠ Head movement could be more controlled")
        
        # Hand motion analysis
        if 'hand_motion' in analysis_results and 'error' not in analysis_results['hand_motion']:
            hand_data = analysis_results['hand_motion']
            activity_level = hand_data.get('activity_level', 'low')
            
            if activity_level == 'moderate':
                scores['hand_gestures'] = 85
                feedback.append("✓ Good use of hand gestures")
            elif activity_level == 'high':
                scores['hand_gestures'] = 70
                feedback.append("→ Consider reducing excessive hand movements")
            else:
                scores['hand_gestures'] = 60
                feedback.append("→ Could use more hand gestures for emphasis")
        
        # Calculate overall body language score
        if scores:
            overall_score = np.mean(list(scores.values()))
        else:
            overall_score = 50
            feedback.append("⚠ Unable to analyze body language - check video quality")
        
        return {
            'overall_score': round(overall_score, 1),
            'detailed_scores': scores,
            'feedback': feedback,
            'category': 'Body Language & Posture'
        }
    
    def evaluate_vocal_delivery(self, analysis_results: Dict, transcript: str = None) -> Dict:
        """Evaluate vocal delivery and speech patterns"""
        scores = {}
        feedback = []
        
        # Disfluency analysis
        if 'disfluency' in analysis_results and 'error' not in analysis_results['disfluency']:
            disfluency_data = analysis_results['disfluency']
            
            # Calculate disfluency rate
            if transcript:
                word_count = len(transcript.split())
                total_disfluencies = disfluency_data.get('total_disfluencies', 0)
                disfluency_rate = (total_disfluencies / word_count) * 100 if word_count > 0 else 0
                
                if disfluency_rate < 2:
                    scores['fluency'] = 95
                    feedback.append("✓ Excellent speech fluency")
                elif disfluency_rate < 5:
                    scores['fluency'] = 80
                    feedback.append("✓ Good speech fluency")
                elif disfluency_rate < 10:
                    scores['fluency'] = 65
                    feedback.append("→ Some disfluencies present, practice for smoother delivery")
                else:
                    scores['fluency'] = 45
                    feedback.append("⚠ High disfluency rate - practice to reduce filler words")
        
        # Speech pace (if available)
        if transcript:
            word_count = len(transcript.split())
            # Assume average speaking time based on video duration
            estimated_duration = analysis_results.get('body_rotation', {}).get('duration_seconds', 60)
            words_per_minute = (word_count / estimated_duration) * 60 if estimated_duration > 0 else 0
            
            if 140 <= words_per_minute <= 180:
                scores['pace'] = 90
                feedback.append("✓ Optimal speaking pace")
            elif 120 <= words_per_minute < 140 or 180 < words_per_minute <= 200:
                scores['pace'] = 75
                feedback.append("→ Speaking pace is acceptable, could be optimized")
            else:
                scores['pace'] = 60
                if words_per_minute < 120:
                    feedback.append("→ Consider speaking a bit faster")
                else:
                    feedback.append("→ Consider slowing down your speaking pace")
        
        # Calculate overall vocal delivery score
        if scores:
            overall_score = np.mean(list(scores.values()))
        else:
            overall_score = 50
            feedback.append("⚠ Unable to analyze vocal delivery - check audio quality")
        
        return {
            'overall_score': round(overall_score, 1),
            'detailed_scores': scores,
            'feedback': feedback,
            'category': 'Vocal Delivery & Speech'
        }
    
    def evaluate_content_quality(self, analysis_results: Dict) -> Dict:
        """Evaluate content quality based on AI analysis"""
        scores = {}
        feedback = []
        
        if 'content' in analysis_results and 'error' not in analysis_results['content']:
            content_data = analysis_results['content']
            
            # Extract content quality metrics if available
            if 'presentationAnalysis' in content_data:
                metrics = content_data['presentationAnalysis'].get('contentQualityMetrics', {})
                
                for metric, data in metrics.items():
                    if isinstance(data, dict) and 'score' in data:
                        score = data['score']
                        scores[metric] = score * 10  # Convert to 0-100 scale
                        
                        # Add feedback based on score
                        if score >= 8:
                            feedback.append(f"✓ Excellent {metric}")
                        elif score >= 6:
                            feedback.append(f"→ Good {metric}, room for improvement")
                        else:
                            feedback.append(f"⚠ {metric} needs significant improvement")
                
                # Overall content score
                overall_content_score = content_data['presentationAnalysis'].get('overallScore', 50)
                scores['overall_content'] = overall_content_score * 10
        
        # Calculate overall content quality score
        if scores:
            overall_score = np.mean(list(scores.values()))
        else:
            overall_score = 50
            feedback.append("⚠ Unable to analyze content quality - ensure clear audio")
        
        return {
            'overall_score': round(overall_score, 1),
            'detailed_scores': scores,
            'feedback': feedback,
            'category': 'Content Quality & Structure'
        }
    
    def evaluate_facial_expression(self, analysis_results: Dict) -> Dict:
        """Evaluate facial expressions and engagement"""
        scores = {}
        feedback = []
        
        if 'expression' in analysis_results and 'error' not in analysis_results['expression']:
            expr_data = analysis_results['expression']
            average_scores = expr_data.get('average_scores', {})
            
            # Analyze emotion distribution
            positive_emotions = ['Happy', 'Surprise']
            neutral_emotions = ['Neutral']
            negative_emotions = ['Angry', 'Sad']
            
            positive_score = sum(average_scores.get(emotion, 0) for emotion in positive_emotions)
            neutral_score = sum(average_scores.get(emotion, 0) for emotion in neutral_emotions)
            negative_score = sum(average_scores.get(emotion, 0) for emotion in negative_emotions)
            
            # Ideal: moderate positive, some neutral, minimal negative
            if positive_score > 0.3 and neutral_score > 0.4 and negative_score < 0.2:
                scores['emotional_engagement'] = 90
                feedback.append("✓ Excellent emotional engagement")
            elif positive_score > 0.2 and negative_score < 0.3:
                scores['emotional_engagement'] = 75
                feedback.append("✓ Good emotional expression")
            else:
                scores['emotional_engagement'] = 60
                feedback.append("→ Consider showing more positive engagement")
            
            # Expressiveness (variety in emotions)
            emotion_variety = len([score for score in average_scores.values() if score > 0.1])
            if emotion_variety >= 3:
                scores['expressiveness'] = 85
                feedback.append("✓ Good range of expressions")
            elif emotion_variety >= 2:
                scores['expressiveness'] = 70
                feedback.append("→ Decent expressiveness")
            else:
                scores['expressiveness'] = 55
                feedback.append("→ Could show more varied expressions")
        
        # Calculate overall facial expression score
        if scores:
            overall_score = np.mean(list(scores.values()))
        else:
            overall_score = 50
            feedback.append("⚠ Unable to analyze facial expressions - ensure face is visible")
        
        return {
            'overall_score': round(overall_score, 1),
            'detailed_scores': scores,
            'feedback': feedback,
            'category': 'Facial Expression & Engagement'
        }
    
    def evaluate_technical_aspects(self, analysis_results: Dict) -> Dict:
        """Evaluate technical quality of the presentation"""
        scores = {}
        feedback = []
        
        # Video quality (based on detection rates)
        detection_rates = []
        for analyzer in ['body_rotation', 'head_motion', 'expression']:
            if analyzer in analysis_results and 'error' not in analysis_results[analyzer]:
                rate = analysis_results[analyzer].get('detection_rate', 0)
                detection_rates.append(rate)
        
        if detection_rates:
            avg_detection = np.mean(detection_rates)
            if avg_detection > 0.9:
                scores['video_quality'] = 95
                feedback.append("✓ Excellent video quality")
            elif avg_detection > 0.7:
                scores['video_quality'] = 80
                feedback.append("✓ Good video quality")
            else:
                scores['video_quality'] = 60
                feedback.append("→ Consider improving video quality/lighting")
        
        # Audio quality (based on transcription success)
        if 'content' in analysis_results and 'error' not in analysis_results['content']:
            scores['audio_quality'] = 90
            feedback.append("✓ Good audio quality")
        elif 'disfluency' in analysis_results and 'error' not in analysis_results['disfluency']:
            scores['audio_quality'] = 75
            feedback.append("✓ Acceptable audio quality")
        else:
            scores['audio_quality'] = 50
            feedback.append("⚠ Audio quality issues detected")
        
        # Calculate overall technical score
        if scores:
            overall_score = np.mean(list(scores.values()))
        else:
            overall_score = 50
            feedback.append("⚠ Technical quality assessment unavailable")
        
        return {
            'overall_score': round(overall_score, 1),
            'detailed_scores': scores,
            'feedback': feedback,
            'category': 'Technical Quality'
        }
    
    def calculate_overall_score(self, category_scores: Dict) -> Dict:
        """Calculate the final overall presentation score"""
        weighted_score = 0
        total_weight = 0
        
        category_mapping = {
            'body_language': 'Body Language & Posture',
            'vocal_delivery': 'Vocal Delivery & Speech',
            'content_quality': 'Content Quality & Structure',
            'facial_expression': 'Facial Expression & Engagement',
            'technical_aspects': 'Technical Quality'
        }
        
        for weight_key, weight in self.weights.items():
            category_name = category_mapping[weight_key]
            if category_name in category_scores:
                score = category_scores[category_name]['overall_score']
                weighted_score += score * weight
                total_weight += weight
        
        # Normalize if some categories are missing
        if total_weight > 0:
            final_score = weighted_score / total_weight
        else:
            final_score = 50
        
        # Determine grade
        grade = self.get_grade(final_score)
        
        return {
            'overall_score': round(final_score, 1),
            'grade': grade,
            'total_possible': 100,
            'category_weights': self.weights,
            'evaluated_categories': len(category_scores)
        }
    
    def get_grade(self, score: float) -> str:
        """Convert numerical score to letter grade"""
        for grade, (min_score, max_score) in self.score_ranges.items():
            if min_score <= score <= max_score:
                return grade.replace('_', ' ').title()
        return "Needs Improvement"
    
    def generate_improvement_suggestions(self, category_scores: Dict, overall_score: float) -> List[str]:
        """Generate personalized improvement suggestions"""
        suggestions = []
        
        # Find weakest categories
        scores_by_category = [(cat, data['overall_score']) for cat, data in category_scores.items()]
        scores_by_category.sort(key=lambda x: x[1])
        
        # Top 3 improvement areas
        for category, score in scores_by_category[:3]:
            if score < 70:
                if 'Body Language' in category:
                    suggestions.append("🎯 Practice maintaining steady posture and using purposeful gestures")
                elif 'Vocal Delivery' in category:
                    suggestions.append("🎯 Work on reducing filler words and maintaining optimal speaking pace")
                elif 'Content Quality' in category:
                    suggestions.append("🎯 Focus on clearer structure and more engaging content delivery")
                elif 'Facial Expression' in category:
                    suggestions.append("🎯 Practice showing more varied and positive facial expressions")
                elif 'Technical Quality' in category:
                    suggestions.append("🎯 Improve recording setup with better lighting and audio equipment")
        
        # Overall suggestions based on total score
        if overall_score < 60:
            suggestions.append("📚 Consider taking a presentation skills course or workshop")
            suggestions.append("🎥 Record yourself practicing to identify areas for improvement")
        elif overall_score < 80:
            suggestions.append("✨ You're doing well! Focus on polishing your weaker areas")
            suggestions.append("🎤 Practice with friends or colleagues for feedback")
        else:
            suggestions.append("🌟 Excellent work! Consider mentoring others or advanced techniques")
        
        return suggestions[:5]  # Limit to top 5 suggestions
    
    def evaluate_presentation(self, analysis_results: Dict, transcript: str = None) -> Dict:
        """Main method to evaluate the entire presentation"""
        evaluation_timestamp = datetime.now().isoformat()
        
        # Evaluate each category
        category_evaluations = {}
        
        # Body Language
        body_eval = self.evaluate_body_language(analysis_results)
        category_evaluations[body_eval['category']] = body_eval
        
        # Vocal Delivery
        vocal_eval = self.evaluate_vocal_delivery(analysis_results, transcript)
        category_evaluations[vocal_eval['category']] = vocal_eval
        
        # Content Quality
        content_eval = self.evaluate_content_quality(analysis_results)
        category_evaluations[content_eval['category']] = content_eval
        
        # Facial Expression
        expression_eval = self.evaluate_facial_expression(analysis_results)
        category_evaluations[expression_eval['category']] = expression_eval
        
        # Technical Aspects
        technical_eval = self.evaluate_technical_aspects(analysis_results)
        category_evaluations[technical_eval['category']] = technical_eval
        
        # Calculate overall score
        overall_evaluation = self.calculate_overall_score(category_evaluations)
        
        # Generate improvement suggestions
        suggestions = self.generate_improvement_suggestions(
            category_evaluations, 
            overall_evaluation['overall_score']
        )
        
        return {
            'evaluation_timestamp': evaluation_timestamp,
            'overall_evaluation': overall_evaluation,
            'category_evaluations': category_evaluations,
            'improvement_suggestions': suggestions,
            'summary': {
                'total_score': overall_evaluation['overall_score'],
                'grade': overall_evaluation['grade'],
                'strengths': self._identify_strengths(category_evaluations),
                'areas_for_improvement': self._identify_weaknesses(category_evaluations)
            }
        }
    
    def _identify_strengths(self, category_evaluations: Dict) -> List[str]:
        """Identify top performing areas"""
        strengths = []
        for category, evaluation in category_evaluations.items():
            if evaluation['overall_score'] >= 80:
                strengths.append(f"{category}: {evaluation['overall_score']:.1f}/100")
        return strengths[:3]  # Top 3 strengths
    
    def _identify_weaknesses(self, category_evaluations: Dict) -> List[str]:
        """Identify areas needing improvement"""
        weaknesses = []
        for category, evaluation in category_evaluations.items():
            if evaluation['overall_score'] < 70:
                weaknesses.append(f"{category}: {evaluation['overall_score']:.1f}/100")
        return weaknesses[:3]  # Top 3 areas for improvement
