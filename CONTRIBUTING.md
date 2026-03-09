# Contributing to Mastering ERPNext Development

Thank you for your interest in contributing to this educational resource! This guide will help you understand how to contribute effectively.

## 🎯 Our Mission

This book aims to be the most comprehensive, practical, and up-to-date resource for ERPNext developers. We welcome contributions that:

- Improve code examples and make them more robust
- Add real-world scenarios and use cases
- Fix errors or outdated information
- Enhance explanations and clarity
- Add new relevant topics as the framework evolves

## 🤝 How to Contribute

### Reporting Issues

1. **Code Issues**: If you find bugs in code examples, please open an issue with:
   - Chapter and file reference
   - Expected vs actual behavior
   - Environment details (Frappe/ERPNext version)
   - Error messages or screenshots

2. **Content Issues**: For documentation errors or unclear explanations:
   - Chapter and section reference
   - Specific problem description
   - Suggested improvement if possible

### Submitting Changes

#### 1. Fork and Clone

```bash
git clone https://github.com/your-username/mastering-erpnext-dev.git
cd mastering-erpnext-dev
```

#### 2. Create a Branch

```bash
git checkout -b fix/chapter-5-orm-example
```

#### 3. Make Your Changes

- **Code Examples**: Ensure they follow Frappe best practices
- **Documentation**: Use clear, concise language
- **New Content**: Align with existing style and structure

#### 4. Test Your Changes

- Run code examples in a test environment
- Verify all instructions work as described
- Check formatting and consistency

#### 5. Submit Pull Request

- Use descriptive titles and commit messages
- Reference related issues
- Describe what you changed and why

## 📝 Contribution Guidelines

### Code Standards

#### Python Code
```python
# Follow PEP 8
# Use descriptive variable names
# Include docstrings for functions
# Handle errors appropriately

def get_asset_with_assignments(asset_id):
    """
    Get asset document with its assignment records.
    
    Args:
        asset_id (str): ID of the asset document
        
    Returns:
        dict: Asset data with assignments
    """
    try:
        asset = frappe.get_doc("Asset", asset_id)
        return asset.as_dict()
    except frappe.DoesNotExistError:
        frappe.throw(f"Asset {asset_id} not found")
```

#### JavaScript Code
```javascript
// Use modern ES6+ syntax
// Handle errors gracefully
// Include comments for complex logic

frappe.ui.form.on('Asset', {
    refresh: function(frm) {
        // Add custom button if asset is available
        if (frm.doc.status === 'Available') {
            frm.add_custom_button(__('Assign Asset'), function() {
                show_assignment_dialog(frm);
            });
        }
    }
});
```

### Documentation Style

#### Headings
- Use `#` for main titles
- Use `##` for chapter sections
- Use `###` for subsections

#### Code Blocks
- Specify language for syntax highlighting
```python
# Python example
```

```javascript
// JavaScript example
```

#### Links and References
- Use descriptive link text
- Reference official Frappe documentation when relevant

### File Organization

- Keep examples in their respective chapter directories
- Use descriptive filenames
- Follow the established directory structure

## 🏷️ Label System

We use labels to categorize contributions:

- `bug-fix`: Error corrections
- `enhancement`: New content or improvements
- `code-example`: Code-related changes
- `documentation`: Text and explanation updates
- `typo`: Spelling and grammar fixes

## 📋 Review Process

1. **Initial Review**: Maintainers check for adherence to guidelines
2. **Technical Review**: Code examples are tested for accuracy
3. **Content Review**: Educational value and clarity assessment
4. **Final Approval**: Changes are merged into main branch

## 🎨 Types of Contributions We Welcome

### Code Examples
- Improved error handling
- Performance optimizations
- Additional use cases
- Edge case coverage

### Documentation
- Concept explanations
- Step-by-step tutorials
- Best practice summaries
- Troubleshooting guides

### New Topics
- Emerging Frappe features
- Advanced techniques
- Industry-specific applications
- Integration examples

## 🚫 What We Don't Accept

- Off-topic content
- Promotional material
- Copyrighted material without permission
- Incomplete or untested examples

## 📧 Getting Help

If you need help contributing:

1. Check existing issues and discussions
2. Start a discussion in the repository
3. Reach out to maintainers

## 🙏 Recognition

Contributors are recognized in:

- Contributors section in the book
- GitHub contributor list
- Release notes for significant contributions

## 📄 License

By contributing, you agree that your contributions will be licensed under the same MIT License as the project.

---

Thank you for helping make ERPNext development education better for everyone! 🎉
