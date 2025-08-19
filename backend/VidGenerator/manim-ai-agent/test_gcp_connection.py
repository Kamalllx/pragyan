#!/usr/bin/env python3
"""
Test the new Google Gen AI SDK with Vertex AI
"""

def test_new_genai_sdk():
    """Test the new Google Gen AI SDK"""
    
    print("🧪 TESTING NEW GOOGLE GEN AI SDK")
    print("=" * 50)
    
    try:
        from google import genai
        from google.genai import types
        print("✅ Google Gen AI SDK imported successfully")
        
        # Create client with Vertex AI
        client = genai.Client(
            vertexai=True,
            project="warp-ai-hackathon",
            location="global",  # Use global location
        )
        print("✅ Client created successfully")
        
        # Test with a simple prompt
        print("\n🧪 Testing model generation...")
        
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part(text="Write a simple Python function that adds two numbers.")
                ]
            )
        ]
        
        generate_content_config = types.GenerateContentConfig(
            temperature=0.2,
            max_output_tokens=500,
        )
        
        model = "gemini-2.5-pro"
        print(f"🤖 Using model: {model}")
        
        # Test streaming generation
        print("\n📝 Generated response:")
        print("-" * 30)
        
        response_text = ""
        for chunk in client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config,
        ):
            print(chunk.text, end="")
            response_text += chunk.text
        
        print("\n" + "-" * 30)
        print("✅ SUCCESS! New Gen AI SDK is working!")
        
        return True, response_text
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False, str(e)

if __name__ == "__main__":
    success, result = test_new_genai_sdk()
    
    if success:
        print("\n🎉 You're ready to use the new SDK!")
        print("\n💡 Key changes:")
        print("  - Use 'pip install google-genai'")
        print("  - Use 'gcloud auth application-default login'")
        print("  - Use location='global'")
        print("  - Use gemini-2.5-flash model")
    else:
        print(f"\n❌ Setup failed: {result}")
