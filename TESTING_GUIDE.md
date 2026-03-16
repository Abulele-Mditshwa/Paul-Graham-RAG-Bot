# 🧪 Testing Guide for Paul Graham Essays RAG System

This guide provides step-by-step instructions for testing the RAG system locally.

## 🚨 Prerequisites (CRITICAL)

**⚠️ You CANNOT use the default configuration - it belongs to the original developer**

Before testing, you MUST set up your own AWS resources:

### 1. AWS Account Setup
- Ensure you have an AWS account with appropriate permissions
- Configure AWS credentials using one of these methods:
  - AWS CLI: `aws configure`
  - Environment variables: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
  - IAM roles (if running on EC2)

### 2. AWS Bedrock Model Access
- Go to AWS Bedrock Console → Model Access
- Request access to **Claude 3 Haiku** (`anthropic.claude-3-haiku-20240307-v1:0`)
- Request access to **Amazon Titan Text Embeddings G1** (`amazon.titan-embed-text-v1`)
- Wait for approval (usually instant for these models)

### 3. Create Your Own Knowledge Base
Follow the detailed setup guide in `README.md` under "AWS Bedrock Knowledge Base Setup" to create:
- Your own Bedrock Knowledge Base with Paul Graham essays
- Your own OpenSearch Serverless collection
- Note down the Knowledge Base ID and collection details

## 🔧 Local Setup

### 1. Clone and Install Dependencies
```bash
git clone <repository-url>
cd paul-graham-rag-system
pip install -r requirements.txt
```

### 2. Configure Your AWS Resources
Choose one of these methods:

#### Option A: Environment Variables (Recommended)
```bash
export KNOWLEDGE_BASE_ID="your_knowledge_base_id"
export OPENSEARCH_COLLECTION_NAME="your_collection_name"
export AWS_REGION="us-east-1"  # or your preferred region
export LLM_MODEL_ID="anthropic.claude-3-haiku-20240307-v1:0"
```

#### Option B: Modify Configuration File
Edit `src/config.py` and replace the default values with your own:
```python
knowledge_base_id: str = "YOUR_KNOWLEDGE_BASE_ID"
opensearch_collection_name: str = "YOUR_COLLECTION_NAME"
aws_region: str = "YOUR_PREFERRED_REGION"
```

## 🧪 Testing Steps

### 1. Test AWS Connection
```bash
python test_knowledge_base.py
```

**Expected Output:**
```
✅ Knowledge Base connection successful
✅ Model access confirmed
✅ System ready for testing
```

**If you see errors:**
- Check your AWS credentials
- Verify Knowledge Base ID is correct
- Ensure model access is granted in Bedrock console

### 2. Run the Streamlit Application
```bash
streamlit run app.py
```

**Expected Behavior:**
- Browser opens to `http://localhost:8501`
- Application loads without errors
- System status shows "Connected" in the sidebar

### 3. Test System Connection (In App)
- Click "Test Connection" button in the sidebar
- Should show green checkmarks for all components
- If any component fails, check your configuration

### 4. Test Chat Functionality

#### Basic Questions to Try:
1. **"What is founder mode?"** - Tests recent essay retrieval
2. **"How do I get startup ideas?"** - Tests classic startup advice
3. **"What makes a great essay?"** - Tests writing advice content
4. **"Tell me about Y Combinator"** - Tests entrepreneurship content
5. **"What is the maker's schedule?"** - Tests productivity concepts

#### Expected Response Format:
- AI-generated answer based on Paul Graham's essays
- Source citations showing which essays were referenced
- Response time typically 2-5 seconds

### 5. Test Source Citations
- Each response should include "Sources" section
- Sources should show essay titles and relevant excerpts
- Click on source links to verify they reference actual Paul Graham essays

### 6. Test Conversation Flow
- Ask follow-up questions to test conversation continuity
- Example flow:
  1. "What is founder mode?"
  2. "Can you give me specific examples?"
  3. "How does this apply to small startups?"

## 🔍 Troubleshooting Common Issues

### Issue: "ModuleNotFoundError"
**Solution:** Ensure you're running from the project root directory and have installed all dependencies:
```bash
pip install -r requirements.txt
```

### Issue: "Knowledge Base not found"
**Solution:** 
- Verify your Knowledge Base ID is correct
- Check that the Knowledge Base exists in the specified AWS region
- Ensure your AWS credentials have access to Bedrock

### Issue: "Access denied to model"
**Solution:**
- Go to AWS Bedrock Console → Model Access
- Request access to Claude 3 Haiku and Titan Embeddings
- Wait for approval and try again

### Issue: "No response from Knowledge Base"
**Solution:**
- Check that your Knowledge Base has been successfully ingested with data
- Verify the Knowledge Base status is "Active" in AWS console
- Try simpler questions first

### Issue: Slow responses
**Expected:** First query may take 10-15 seconds (cold start)
**Normal:** Subsequent queries should be 2-5 seconds
**If consistently slow:** Check your AWS region and network connection

## 📊 Performance Expectations

### Response Times:
- **First query:** 10-15 seconds (cold start)
- **Subsequent queries:** 2-5 seconds
- **System connection test:** 3-5 seconds

### Accuracy Expectations:
- Responses should be grounded in Paul Graham's actual essays
- Source citations should be relevant to the question
- AI should acknowledge when information isn't available in the essays

## 🎯 Test Scenarios

### Scenario 1: Startup Advice
**Question:** "How should I validate my startup idea?"
**Expected:** Response about customer development, talking to users, building MVPs
**Sources:** Should reference essays like "Do Things that Don't Scale"

### Scenario 2: Writing Advice  
**Question:** "How do I write better essays?"
**Expected:** Advice about clarity, simplicity, and authentic voice
**Sources:** Should reference "Writing, Briefly" or similar essays

### Scenario 3: Y Combinator Insights
**Question:** "What makes a successful Y Combinator application?"
**Expected:** Insights about team, idea, and execution
**Sources:** Should reference YC-related essays

### Scenario 4: Edge Cases
**Question:** "What does Paul Graham think about cryptocurrency?"
**Expected:** Either relevant content if available, or acknowledgment that the topic isn't covered extensively

## 📝 Success Criteria

✅ **Application starts without errors**  
✅ **System connection test passes**  
✅ **Chat interface responds to questions**  
✅ **Responses include relevant source citations**  
✅ **Sources reference actual Paul Graham essays**  
✅ **Response times are reasonable (2-15 seconds)**  
✅ **Conversation flow works with follow-up questions**  
✅ **Error handling works gracefully**

## 🆘 Getting Help

If you encounter issues:

1. **Check the logs:** Streamlit shows errors in the terminal
2. **Verify configuration:** Double-check all AWS resource IDs
3. **Test AWS access:** Use AWS CLI to verify your credentials work
4. **Check AWS console:** Verify Knowledge Base status and model access
5. **Review this guide:** Ensure you've followed all prerequisite steps

## 📋 Quick Checklist

Before reporting issues, verify:

- [ ] AWS credentials are configured correctly
- [ ] You have your own Knowledge Base (not using default IDs)
- [ ] Model access is granted in Bedrock console
- [ ] All dependencies are installed
- [ ] You're running from the correct directory
- [ ] Your Knowledge Base contains Paul Graham essays
- [ ] The Knowledge Base status is "Active" in AWS console

---

**Remember:** This system requires your own AWS resources. The default configuration will NOT work as it uses the original developer's private resources.