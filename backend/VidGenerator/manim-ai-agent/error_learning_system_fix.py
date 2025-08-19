def test_corrected_speakers():
    """Test the corrected speaker configuration"""
    
    # Valid speakers from API error
    valid_speakers = [
        'meera', 'pavithra', 'maitreyi', 'arvind', 'amol', 'amartya', 
        'diya', 'neel', 'misha', 'vian', 'arjun', 'maya', 'anushka', 
        'abhilash', 'manisha', 'vidya', 'arya', 'karun', 'hitesh'
    ]
    
    # Our corrected configuration
    corrected_voices = {
        'hindi': 'meera',
        'english': 'arvind',
        'bengali': 'diya',
        'gujarati': 'maya',
        'kannada': 'arjun',
        'malayalam': 'neel',
        'marathi': 'amol',
        'odia': 'misha',
        'punjabi': 'vian',
        'tamil': 'anushka',
        'telugu': 'vidya',
        'urdu': 'pavithra'
    }
    
    print("🔍 Validating corrected speaker configuration...")
    
    all_valid = True
    for lang, voice in corrected_voices.items():
        if voice in valid_speakers:
            print(f"   ✅ {lang}: {voice}")
        else:
            print(f"   ❌ {lang}: {voice} - INVALID")
            all_valid = False
    
    print(f"\n🎯 All speakers valid: {all_valid}")
    
    # Test chunking
    test_text = "This is a test script that is longer than 500 characters. " * 10
    
    # Simulate chunking
    max_chars = 450
    chunks = []
    
    if len(test_text) <= max_chars:
        chunks = [test_text]
    else:
        words = test_text.split()
        current_chunk = ""
        
        for word in words:
            if len(current_chunk) + len(word) + 1 <= max_chars:
                current_chunk += " " + word if current_chunk else word
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                    current_chunk = word
        
        if current_chunk:
            chunks.append(current_chunk)
    
    print(f"\n📝 Text chunking test:")
    print(f"   Original length: {len(test_text)}")
    print(f"   Chunks created: {len(chunks)}")
    for i, chunk in enumerate(chunks):
        print(f"   Chunk {i+1}: {len(chunk)} chars")
        if len(chunk) > 500:
            print(f"      ❌ Too long!")
        else:
            print(f"      ✅ Valid length")
    
    return all_valid

if __name__ == "__main__":
    test_corrected_speakers()
