"""
Quick Fix for Transformers Compatibility Issue

If you're getting "Unknown task summarization" error, run this script.
"""

def check_transformers_version():
    """Check transformers version and available tasks"""
    try:
        import transformers
        print(f"Transformers version: {transformers.__version__}")
        
        # Try to get available tasks
        try:
            from transformers.pipelines import SUPPORTED_TASKS
            print(f"\nSupported tasks: {list(SUPPORTED_TASKS.keys())[:10]}...")
            
            # Check if summarization is available
            if "summarization" in SUPPORTED_TASKS:
                print("✓ 'summarization' task is available")
            elif "text2text-generation" in SUPPORTED_TASKS:
                print("✓ 'text2text-generation' task is available (alternative)")
            else:
                print("⚠ Neither 'summarization' nor 'text2text-generation' found")
                
        except ImportError:
            print("⚠ Could not import SUPPORTED_TASKS")
            
    except ImportError:
        print("✗ transformers not installed")
        return False
    
    return True


def fix_transformers():
    """Upgrade transformers to latest version"""
    print("\n" + "="*70)
    print("FIXING TRANSFORMERS COMPATIBILITY")
    print("="*70)
    
    import subprocess
    import sys
    
    print("\nUpgrading transformers to latest version...")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", "transformers"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✓ Transformers upgraded successfully")
            print("\nPlease restart your Python kernel/runtime and try again.")
            return True
        else:
            print(f"✗ Upgrade failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"✗ Error during upgrade: {e}")
        return False


def test_summarization():
    """Test if summarization works"""
    print("\n" + "="*70)
    print("TESTING SUMMARIZATION")
    print("="*70)
    
    try:
        from transformers import pipeline
        
        # Try different task names
        tasks_to_try = ["summarization", "text2text-generation"]
        
        for task in tasks_to_try:
            try:
                print(f"\nTrying task: {task}")
                print("  Loading DistilBART (may take 1-2 minutes on first run)...")
                
                summarizer = pipeline(task, model="sshleifer/distilbart-cnn-12-6")
                
                # Test it
                test_text = "This is a test document. It contains multiple sentences to test the summarization capability. We want to ensure the model works correctly."
                result = summarizer(test_text, max_length=30, min_length=10, do_sample=False)
                
                print(f"✓ {task} works!")
                print(f"  Test summary: {result[0]['summary_text']}")
                return True
                
            except Exception as e:
                error = str(e)
                if "Unknown task" in error:
                    print(f"  ✗ {task} not available")
                else:
                    print(f"  ✗ Error: {error[:100]}")
                continue
        
        print("\n⚠ Neither task type worked")
        print("Trying direct model loading as fallback...")
        
        # Try direct loading
        try:
            from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
            
            model_name = "sshleifer/distilbart-cnn-12-6"
            print(f"  Loading {model_name} directly...")
            
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
            
            # Test it
            test_text = "This is a test document. It contains multiple sentences."
            inputs = tokenizer(test_text, return_tensors="pt", max_length=1024, truncation=True)
            summary_ids = model.generate(inputs["input_ids"], max_length=30, min_length=10, num_beams=4)
            summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
            
            print("✓ Direct model loading works!")
            print(f"  Test summary: {summary}")
            return True
            
        except Exception as e:
            print(f"✗ Direct loading also failed: {str(e)[:100]}")
            return False
        
    except ImportError:
        print("✗ transformers not installed")
        return False


def main():
    print("="*70)
    print("TRANSFORMERS COMPATIBILITY FIX")
    print("="*70)
    
    # Check current version
    if not check_transformers_version():
        print("\nPlease install transformers: pip install transformers")
        return
    
    # Test if it works
    print("\nTesting current setup...")
    if test_summarization():
        print("\n" + "="*70)
        print("✓ EVERYTHING WORKING!")
        print("="*70)
        print("\nYour transformers installation is working correctly.")
        print("You can now use the compression engine.")
        return
    
    # Offer to upgrade
    print("\n" + "="*70)
    response = input("\nUpgrade transformers to fix compatibility? [y/N]: ")
    
    if response.lower() == 'y':
        if fix_transformers():
            print("\n" + "="*70)
            print("NEXT STEPS:")
            print("="*70)
            print("1. Restart your Python kernel/runtime")
            print("2. Run this script again to verify")
            print("3. If working, proceed with the compression engine")
    else:
        print("\n" + "="*70)
        print("ALTERNATIVE SOLUTION:")
        print("="*70)
        print("The compression engine will work with GETS extractive summarization.")
        print("You'll get:")
        print("  ✓ Full hierarchical compression")
        print("  ✓ All critical facts extracted")
        print("  ✓ Complete traceability")
        print("  ✓ Contradiction detection")
        print("  ⚠ Extractive summaries (exact sentences) instead of abstractive")
        print("\nThis is still fully functional for enterprise use!")


if __name__ == "__main__":
    main()
