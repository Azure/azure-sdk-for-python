# Azure AI Content Understanding Python SDK Samples

This directory contains comprehensive Python samples demonstrating how to use the Azure AI Content Understanding service with the Python SDK.

## 📋 Overview

The Azure AI Content Understanding service provides powerful AI capabilities for analyzing and understanding content. These samples cover three main areas:

### 🎯 **Content Analysis**
- Analyze documents and images for layout, text, tables, and structural elements
- Extract structured data from various document types
- Process both binary files and text content

### 🏷️ **Content Classification** 
- Classify documents into predefined categories
- Create and manage custom classifiers
- Train models for domain-specific classification tasks

### 👤 **Face Recognition & Person Management**
- Manage person directories for face recognition
- Add, update, and organize faces and persons
- Find similar faces and verify person identity
- Comprehensive face management workflows

## 🚀 Quick Start

### Prerequisites

1. **Azure Content Understanding Resource**
   - Create an Azure Content Understanding resource in the [Azure Portal](https://portal.azure.com)
   - Note your endpoint URL and access key
   - See [Prerequisites Guide](https://learn.microsoft.com/en-us/azure/ai-services/content-understanding/quickstart/use-rest-api?tabs=document#prerequisites)

2. **Python Environment**
   ```bash
   pip install azure-ai-contentunderstanding python-dotenv
   ```

3. **Authentication Setup**
   - Copy `env.sample` to `.env` in your repository root
   - Configure your endpoint and authentication method

### Environment Configuration

```bash
# Copy the sample environment file
cp env.sample .env

# Edit .env with your values
AZURE_CONTENT_UNDERSTANDING_ENDPOINT=https://your-resource-name.services.ai.azure.com/

# Option 1: Use Azure CLI (Recommended)
# Run: az login
# Leave AZURE_CONTENT_UNDERSTANDING_KEY empty

# Option 2: Use Access Key (Testing only)
AZURE_CONTENT_UNDERSTANDING_KEY=your-access-key
```

## 📁 Sample Categories

### Content Analyzers
Analyze documents and extract structured information:

- **`content_analyzers_analyze.py`** - Analyze text content for layout and structure
- **`content_analyzers_analyze_binary.py`** - Analyze binary files (PDFs, images, documents)
- **`content_analyzers_create_or_replace.py`** - Create or update custom analyzers
- **`content_analyzers_get_analyzer.py`** - Retrieve analyzer configurations
- **`content_analyzers_list.py`** - List all available analyzers
- **`content_analyzers_update.py`** - Update existing analyzers
- **`content_analyzers_delete_analyzer.py`** - Delete custom analyzers
- **`content_analyzers_get_operation_status.py`** - Check analysis operation status
- **`content_analyzers_get_result.py`** - Retrieve analysis results
- **`content_analyzers_get_result_file.py`** - Download result files

### Content Classifiers
Classify content into categories:

- **`content_classifiers_classify.py`** - Classify text content
- **`content_classifiers_classify_binary.py`** - Classify binary files
- **`content_classifiers_create_or_replace.py`** - Create or update classifiers
- **`content_classifiers_get_classifier.py`** - Retrieve classifier configurations
- **`content_classifiers_list.py`** - List all available classifiers
- **`content_classifiers_update.py`** - Update existing classifiers
- **`content_classifiers_delete_classifier.py`** - Delete custom classifiers
- **`content_classifiers_get_operation_status.py`** - Check classification operation status
- **`content_classifiers_get_result.py`** - Retrieve classification results

### Face Recognition & Person Management
Comprehensive face recognition capabilities:

#### **Directory Management**
- **`person_directories_create.py`** - Create person directories
- **`person_directories_get.py`** - Retrieve directory information
- **`person_directories_list.py`** - List all directories
- **`person_directories_update.py`** - Update directory properties
- **`person_directories_delete.py`** - Delete directories

#### **Person Management**
- **`person_directories_add_person.py`** - Add persons to directories
- **`person_directories_get_person.py`** - Retrieve person information
- **`person_directories_list_persons.py`** - List all persons in a directory
- **`person_directories_update_person.py`** - Update person properties
- **`person_directories_delete_person.py`** - Delete persons

#### **Face Management**
- **`person_directories_get_face.py`** - Retrieve face information
- **`person_directories_list_faces.py`** - List all faces in a directory
- **`person_directories_update_face.py`** - Update face associations
- **`person_directories_delete_face.py`** - Delete faces

#### **Face Recognition**
- **`person_directories_find_similar_faces.py`** - Find similar faces (⭐ **Enhanced Demo**)
- **`faces_detect.py`** - Detect faces in images

### Special Features

#### **🎯 Enhanced Face Similarity Demo**
`person_directories_find_similar_faces.py` provides a comprehensive demonstration:

- **Test 1 (Positive Case)**: Enrolls Dad1 & Dad2 faces, queries with Dad3 → should find matches
- **Test 2 (Negative Case)**: Queries with Mom1 (different person) → should find no matches
- **Educational Output**: Clear explanations of expected results and confidence scores
- **Real-world Scenarios**: Demonstrates both successful and failed face matching

## 🔧 Running Samples

**⚠️ Important**: Always run samples from the `generated_samples` directory:

```bash
# Navigate to the samples directory first
cd sdk/contentunderstanding/azure-ai-contentunderstanding/generated_samples

# Then run any sample
python person_directories_create.py
python content_analyzers_analyze_binary.py
python person_directories_find_similar_faces.py
```

**Why run from generated_samples directory?**
- Samples use relative paths to find test data and helper files
- Ensures proper import resolution for `sample_helper.py`
- Creates output files in the correct `test_output/` subdirectory

## 📚 Additional Resources

- **[Azure AI Content Understanding Documentation](https://learn.microsoft.com/en-us/azure/ai-services/content-understanding/)**
- **[Python SDK Reference](https://learn.microsoft.com/en-us/python/api/overview/azure/ai-contentunderstanding-readme)**
- **[REST API Reference](https://learn.microsoft.com/en-us/rest/api/contentunderstanding/)**
- **[Quickstart Guide](https://learn.microsoft.com/en-us/azure/ai-services/content-understanding/quickstart/use-rest-api)**

## 🐛 Troubleshooting

### **Authentication Issues**
```bash
# Check Azure CLI login
az account show

# Verify endpoint format
echo $AZURE_CONTENT_UNDERSTANDING_ENDPOINT
# Should be: https://your-resource-name.services.ai.azure.com/
```

### **Missing Dependencies**
```bash
pip install azure-ai-contentunderstanding python-dotenv
```

### **Common Issues**
- **403 Forbidden**: Check your key or Azure CLI authentication
- **404 Not Found**: Verify your endpoint URL is correct
- **Invalid face source**: Ensure image files exist in `../generated_tests/test_data/`

## 🚀 Next Steps

### **Recommended Starting Samples**

We recommend starting with these core API samples that demonstrate the most common use cases:

1. **📄 Document Analysis** - `content_analyzers_analyze_binary.py`
   - Analyze PDFs, images, and documents for content extraction
   - Shows basic document processing workflow
   - Great introduction to Content Understanding APIs

2. **🔧 Custom Analyzer Creation** - `content_analyzers_create_or_replace.py`
   - Create custom analyzers for specific field extraction
   - Demonstrates advanced API configuration
   - Essential for production scenarios

3. **🏷️ Content Classification** - `content_classifiers_classify_binary.py`
   - Classify documents into categories
   - Shows classification workflow end-to-end
   - Useful for content organization

### **Next Steps**

4. **Explore face recognition**: Run `person_directories_find_similar_faces.py` for a comprehensive face API demo
5. **Build custom workflows**: Combine multiple samples for your specific use case
6. **Check output files**: Review saved results in `test_output/` directory for detailed API responses

---

**💡 Pro Tip**: Start with `content_analyzers_analyze_binary.py` - it demonstrates the most fundamental Content Understanding capability and works with any document or image file!
