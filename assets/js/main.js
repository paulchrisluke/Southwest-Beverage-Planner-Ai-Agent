document.addEventListener('DOMContentLoaded', async () => {
    try {
        // Load the research paper content
        const response = await fetch('docs/research_paper.md');
        const markdown = await response.text();
        
        // Split the content into sections
        const sections = markdown.split('# ').filter(Boolean);
        
        // Process each section
        sections.forEach(section => {
            const firstLine = section.split('\n')[0];
            const content = section.split('\n').slice(1).join('\n');
            
            // Map section titles to their respective elements
            if (firstLine.toLowerCase().includes('abstract')) {
                document.querySelector('#abstract').innerHTML = `
                    <h2>Abstract</h2>
                    ${marked.parse(content)}
                `;
            } else if (firstLine.toLowerCase().includes('methodology')) {
                document.querySelector('#methodology').innerHTML = marked.parse(content);
            } else if (firstLine.toLowerCase().includes('results')) {
                document.querySelector('#results').innerHTML = marked.parse(content);
            }
        });
    } catch (error) {
        console.error('Error loading research paper:', error);
    }
}); 