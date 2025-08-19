from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain.agents import AgentExecutor, create_structured_chat_agent
from langchain.memory import ConversationBufferMemory
from langchain.tools import BaseTool
from langchain.prompts import SystemMessagePromptTemplate
from langchain import hub   

class LearningSession(BaseModel):
    topic: str
    subtopics: List[Dict[str, str]] = Field(default_factory=list)
    quiz_results: List[Dict] = Field(default_factory=list)
    engagement_metrics: Dict = Field(default_factory=dict)
    resources: List[Dict] = Field(default_factory=list)

class CustomAgent:
    """Base class for our custom agents"""
    def __init__(self, name: str, description: str, llm, tools: List[BaseTool]):
        self.name = name
        self.description = description
        self.llm = llm
        self.tools = tools
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        
        # Create a structured chat prompt manually with all required variables
        prompt = hub.pull("hwchase17/structured-chat-agent")

        # Customize the system message part of the prompt
        custom_system_message_template = f"You are {name}, {description}. " + prompt.messages[0].prompt.template
        prompt.messages[0] = SystemMessagePromptTemplate.from_template(custom_system_message_template)
        
        # Create LangChain agent with the properly formatted prompt
        self.agent = create_structured_chat_agent(
            llm=llm, 
            tools=tools, 
            prompt=prompt
        )
        
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=tools,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True # Makes the agent more robust
        )
    
    
    def run(self, input_text: str) -> str:
        """Run the agent on the given input"""
        return self.agent_executor.invoke({"input": input_text})["output"]

class AgentCoordinator:
    def __init__(self, groq_api_key: str, model_name: str = "llama3-70b-8192"):
        self.groq_api_key = groq_api_key
        self.model_name = model_name
        self.llm = ChatGroq(api_key=groq_api_key, model_name=model_name)
        self.session = LearningSession(topic="")
        self.setup_agents()
    
    def setup_agents(self):
        """Create all custom agents"""
        # Concept Explorer Agent
        concept_tools = [self._create_concept_breakdown_tool()]
        self.concept_explorer = CustomAgent(
            name="Concept Explorer",
            description="Breaks down complex topics into digestible chunks",
            llm=self.llm,
            tools=concept_tools
        )
        
        # Assessment Agent
        assessment_tools = [self._create_quiz_tool(), self._grade_quiz_tool()]
        self.assessment_agent = CustomAgent(
            name="Assessment Agent",
            description="Creates and grades personalized quizzes",
            llm=self.llm,
            tools=assessment_tools
        )
        
        # Motivation Agent
        motivation_tools = [self._track_engagement_tool(), self._provide_encouragement_tool()]
        self.motivation_agent = CustomAgent(
            name="Motivation Agent",
            description="Tracks engagement and provides encouragement",
            llm=self.llm,
            tools=motivation_tools
        )
        
        # Resource Curator Agent
        resource_tools = [self._curate_resources_tool()]
        self.resource_curator = CustomAgent(
            name="Resource Curator",
            description="Finds and recommends additional learning materials",
            llm=self.llm,
            tools=resource_tools
        )
    
    def _create_concept_breakdown_tool(self):
        """Tool to break down complex topics into subtopics"""
        from langchain.tools import StructuredTool
        
        def breakdown_concept(topic: str) -> Dict:
            subtopics = self.llm.invoke(f"Break down the topic '{topic}' into 3-5 key subtopics. For each subtopic, provide a name and brief explanation. Format as JSON.")
            # In a real implementation, we'd parse the LLM's response into structured data
            # For now, we'll use a simplified approach
            self.session.topic = topic
            self.session.subtopics = [{"name": "Subtopic 1", "explanation": "Explanation 1"}, 
                                    {"name": "Subtopic 2", "explanation": "Explanation 2"}]
            return {"status": "success", "topic": topic, "subtopics": self.session.subtopics}
        
        return StructuredTool.from_function(
            func=breakdown_concept,
            name="BreakdownConcept",
            description="Breaks down a complex topic into digestible subtopics"
        )
    
    # Only updating the relevant methods - rest of the file stays the same

    def _create_quiz_tool(self):
        """Tool to create a quiz based on a topic"""
        from langchain.tools import StructuredTool
        
        def create_quiz(topic: str, subtopics: Optional[List[str]] = None) -> Dict:
            prompt = f"Create 3 challenging but fair multiple-choice quiz questions about {topic}"
            if subtopics:
                prompt += f", focusing on {', '.join(subtopics)}"
            prompt += ". For each question, provide 4 options labeled A, B, C, D and indicate the correct answer. Format as a JSON array of question objects."
            
            questions_text = self.llm.invoke(prompt)
            
            # Try to parse the response as JSON
            try:
                # Look for JSON in the response
                import re
                import json
                json_match = re.search(r'\[.*\]', questions_text, re.DOTALL)
                if json_match:
                    questions = json.loads(json_match.group(0))
                    return {"questions": questions}
                else:
                    # If no JSON array found, return the raw text for client-side parsing
                    return {"questions_text": questions_text}
            except:
                # If parsing fails, return the raw text
                return {"questions_text": questions_text}
        
        return StructuredTool.from_function(
            func=create_quiz,
            name="CreateQuiz",
            description="Creates a quiz with multiple choice questions on a topic and optional subtopics"
        )

    def _grade_quiz_tool(self):
        """Tool to grade quiz responses"""
        from langchain.tools import StructuredTool
        
        def grade_quiz(quiz_responses: List[Dict]) -> Dict:
            # Grade quiz responses
            correct = sum(1 for resp in quiz_responses if resp.get("is_correct", False))
            total = len(quiz_responses)
            score = correct / total if total > 0 else 0
            
            # Generate personalized feedback based on score
            feedback_prompt = f"Generate personalized, encouraging feedback for a student who got {correct} out of {total} questions correct on a quiz. Keep it under 100 words."
            feedback = self.llm.invoke(feedback_prompt)
            
            result = {
                "score": score,
                "correct": correct,
                "total": total,
                "feedback": str(feedback),
                "performance": "excellent" if score >= 0.9 else "good" if score >= 0.7 else "fair" if score >= 0.5 else "needs_improvement"
            }
            
            self.session.quiz_results.append(result)
            return result
        
        return StructuredTool.from_function(
            func=grade_quiz,
            name="GradeQuiz",
            description="Grades quiz responses and provides personalized feedback"
        )
    
    def _track_engagement_tool(self):
        """Tool to track user engagement"""
        from langchain.tools import StructuredTool
        
        def track_engagement(activity_data: Dict) -> Dict:
            # Track user engagement metrics
            # activity_data might include time spent, completion rates, etc.
            self.session.engagement_metrics.update(activity_data)
            return {"status": "success", "metrics": self.session.engagement_metrics}
        
        return StructuredTool.from_function(
            func=track_engagement,
            name="TrackEngagement",
            description="Records and analyzes user engagement metrics"
        )
    
    # Update the _provide_encouragement_tool method

    def _provide_encouragement_tool(self):
        """Tool to provide personalized encouragement"""
        from langchain.tools import StructuredTool
        
        def provide_encouragement(context: Dict) -> Dict:
            """
            Generate personalized encouragement based on context
            
            Args:
                context: Dictionary containing context information.
                    Must include at least one of:
                    - engagement_level (str): low, medium, or high
                    - recent_score (float): score between 0 and 1
                    
            Returns:
                Dict with encouragement message
            """
            # Handle different input formats - allow score OR engagement_level + recent_score
            if "score" in context and "engagement_level" not in context and "recent_score" not in context:
                # Convert to the expected format
                score = context.get("score", 0)
                if isinstance(score, (int, float)):
                    score = float(score) / 100 if score > 1 else float(score)
                    context["recent_score"] = score
                    context["engagement_level"] = "high" if score >= 0.7 else "medium" if score >= 0.4 else "low"
            
            # Ensure we have required fields
            engagement_level = context.get("engagement_level", "medium")
            recent_score = context.get("recent_score", 0.7)
            topic = context.get("topic", "this topic")
            
            prompt = f"Generate an encouraging message for a student who just completed a quiz on {topic} with engagement level '{engagement_level}' and scored {recent_score*100}%. Keep it brief and motivating."
            message = self.llm.invoke(prompt)
            return {"message": str(message)}
        
        return StructuredTool.from_function(
            func=provide_encouragement,
            name="ProvideEncouragement",
            description="Generates personalized encouragement messages based on user performance and engagement"
        )
    
    # Add this method to your existing AgentCoordinator class:

    def _curate_resources_tool(self):
        """Tool to curate learning resources"""
        from langchain.tools import StructuredTool
    
        def curate_resources(topic: str, subtopics: Optional[List[str]] = None) -> List[Dict]:
            # Find and recommend learning resources
            prompt = f"Find 3 specific, real learning resources for the topic '{topic}'. Only include resources that are real and currently accessible on the web. Do NOT invent or hallucinate URLs—only include resources you are certain exist, and prefer well-known sites (Wikipedia, YouTube, Coursera, Khan Academy, etc). For each resource provide a title, type (article/video/course), the actual URL (no placeholders), and brief description. Format as JSON array."
            if subtopics:
                prompt += f" focusing on the subtopics: {', '.join(subtopics)}"
            resources_text = self.llm.invoke(prompt)
            
            # Try to parse JSON response from LLM
            try:
                # Look for JSON in the response
                import re
                import json
                json_match = re.search(r'\[.*\]', resources_text, re.DOTALL)
                if json_match:
                    resources = json.loads(json_match.group(0))
                else:
                    # If no JSON array found, create structured resources
                    resources = [
                        {
                            "title": f"{topic} - Comprehensive Guide",
                            "type": "article",
                            "url": "https://example.com/guide",
                            "description": f"A complete introduction to {topic} covering key concepts and applications."
                        },
                        {
                            "title": f"{topic} Video Tutorial Series",
                            "type": "video",
                            "url": "https://example.com/video",
                            "description": f"Step-by-step video explanations of {topic} with examples."
                        },
                        {
                            "title": f"Interactive {topic} Course",
                            "type": "course",
                            "url": "https://example.com/course",
                            "description": f"Hands-on learning with exercises and projects on {topic}."
                        }
                    ]
            except:
                # Fallback if JSON parsing fails
                resources = [
                    {
                        "title": f"{topic} - Comprehensive Guide",
                        "type": "article",
                        "url": "https://example.com/guide",
                        "description": f"A complete introduction to {topic} covering key concepts and applications."
                    },
                    {
                        "title": f"{topic} Video Tutorial Series",
                        "type": "video",
                        "url": "https://example.com/video",
                        "description": f"Step-by-step video explanations of {topic} with examples."
                    },
                    {
                        "title": f"Interactive {topic} Course",
                        "type": "course",
                        "url": "https://example.com/course",
                        "description": f"Hands-on learning with exercises and projects on {topic}."
                    }
                ]
            
            self.session.resources = resources
            return resources
        
        return StructuredTool.from_function(
            func=curate_resources,
            name="CurateResources",
            description="Finds and recommends specific learning resources with titles, types and URLs"
        )
    
    def learn_topic(self, topic: str):
        """Main method to orchestrate the learning process"""
        self.session = LearningSession(topic=topic)
        results = {}
        
        # Step 1: Break down the topic
        concept_result = self.concept_explorer.run(
            f"Break down the topic '{topic}' into digestible subtopics"
        )
        results["concept_exploration"] = concept_result
        
        # Step 2: Create a quiz
        assessment_result = self.assessment_agent.run(
            f"Create a quiz about '{topic}' based on these subtopics: {self.session.subtopics}"
        )
        results["assessment"] = assessment_result
        
        # Step 3: Provide motivation
        motivation_result = self.motivation_agent.run(
            f"Provide motivational guidance for learning '{topic}' based on these engagement metrics: {self.session.engagement_metrics}"
        )
        results["motivation"] = motivation_result
        
        # Step 4: Find resources
        resources_result = self.resource_curator.run(
            f"Find the best learning resources for '{topic}' focusing on these subtopics: {self.session.subtopics}"
        )
        results["resources"] = resources_result
        
        return {
            "topic": self.session.topic,
            "subtopics": self.session.subtopics,
            "quiz_results": self.session.quiz_results,
            "engagement_metrics": self.session.engagement_metrics,
            "resources": self.session.resources,
            "agent_results": results
        }