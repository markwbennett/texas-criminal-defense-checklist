import { ChecklistItem, CaseTemplate } from '../types/checklist';

// Count leading spaces to determine indentation level
const getIndentationLevel = (line: string): number => {
  const match = line.match(/^\s*/);
  return match ? Math.floor(match[0].length / 2) : 0;
};

// Extract the title from a line (remove leading spaces)
const extractTitle = (line: string): string => {
  return line.trim();
};

// Generate a unique ID for an item
const generateId = (title: string, level: number): string => {
  return `${level}-${title.toLowerCase().replace(/\s+/g, '-')}`;
};

// Parse plain text into a hierarchical checklist structure
export const parseChecklistText = (text: string, name: string): CaseTemplate => {
  const lines = text.split('\n').filter(line => line.trim() !== '');
  const rootItems: ChecklistItem[] = [];
  const stack: { item: ChecklistItem; level: number }[] = [];
  
  lines.forEach(line => {
    const level = getIndentationLevel(line);
    const title = extractTitle(line);
    const id = generateId(title, level);
    
    const newItem: ChecklistItem = {
      id,
      title,
      isComplete: false,
      children: [],
      dependencies: [],
      dependents: [],
      level,
      hasSubChecklist: false
    };
    
    // If this is a root item (level 0)
    if (level === 0) {
      rootItems.push(newItem);
      stack.length = 0; // Clear the stack
      stack.push({ item: newItem, level });
    } else {
      // Find the appropriate parent
      while (stack.length > 0 && stack[stack.length - 1].level >= level) {
        stack.pop();
      }
      
      if (stack.length > 0) {
        const parent = stack[stack.length - 1].item;
        parent.children.push(newItem);
        
        // If parent is level 0 and this is level 1, mark parent as having a sub-checklist
        if (parent.level === 0 && level === 1) {
          parent.hasSubChecklist = true;
          newItem.linkedChecklistId = `checklist-${id}`;
        }
      } else {
        // If no parent found, add to root
        rootItems.push(newItem);
      }
      
      stack.push({ item: newItem, level });
    }
  });
  
  return {
    id: `template-${name.toLowerCase().replace(/\s+/g, '-')}`,
    name,
    description: `Checklist created from text input`,
    rootItems,
    sourceText: text
  };
}; 