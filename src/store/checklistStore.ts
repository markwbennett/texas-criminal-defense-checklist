import { create } from 'zustand';
import { ChecklistItem, Case, CaseTemplate } from '../types/checklist';

interface ChecklistStore {
  cases: Case[];
  templates: CaseTemplate[];
  
  addCase: (templateId: string, name: string) => string | null;
  toggleItem: (caseId: string, itemId: string) => void;
  updateLinkedChecklistProgress: (caseId: string, itemId: string, percentage: number) => void;
  getLinkedChecklistProgress: (caseId: string, itemId: string) => number;
  createSubChecklist: (parentCaseId: string, parentItemId: string, items: ChecklistItem[]) => string | null;
  updateParentCompletion: (caseId: string, itemId: string) => void;
  refreshChecklistCompletion: (caseId: string) => void;
}

export const useChecklistStore = create<ChecklistStore>((set, get) => ({
  cases: [],
  templates: [],

  addCase: (templateId, name) => {
    const template = get().templates.find(t => t.id === templateId);
    if (!template) return null;

    const newCase: Case = {
      id: crypto.randomUUID(),
      name,
      templateId,
      items: JSON.parse(JSON.stringify(template.rootItems)),
      createdAt: new Date(),
      updatedAt: new Date(),
    };

    set(state => ({ cases: [...state.cases, newCase] }));
    
    // Create sub-checklists for level 1 items
    newCase.items.forEach(item => {
      if (item.hasSubChecklist && item.children.length > 0) {
        const subChecklistId = get().createSubChecklist(newCase.id, item.id, item.children);
        if (subChecklistId) {
          item.linkedChecklistId = subChecklistId;
        }
      }
    });
    
    return newCase.id;
  },

  toggleItem: (caseId, itemId) => {
    set(state => {
      const caseIndex = state.cases.findIndex(c => c.id === caseId);
      if (caseIndex === -1) return state;

      const newCases = [...state.cases];
      const targetCase = { ...newCases[caseIndex] };
      
      const updateItem = (items: ChecklistItem[], currentLevel: number = 0): boolean => {
        for (const item of items) {
          if (item.id === itemId) {
            // Don't toggle if it's a linked checklist item
            if (!item.linkedChecklistId) {
              item.isComplete = !item.isComplete;
              
              // If this is a child item, update parent completion
              if (currentLevel > 0) {
                // Use setTimeout to ensure the state update has completed
                setTimeout(() => {
                  get().updateParentCompletion(caseId, itemId);
                }, 0);
              }
            }
            return true;
          }
          if (updateItem(item.children, currentLevel + 1)) return true;
        }
        return false;
      };

      updateItem(targetCase.items);
      newCases[caseIndex] = targetCase;
      return { cases: newCases };
    });
  },

  updateLinkedChecklistProgress: (caseId, itemId, percentage) => {
    set(state => {
      const caseIndex = state.cases.findIndex(c => c.id === caseId);
      if (caseIndex === -1) return state;

      const newCases = [...state.cases];
      const targetCase = { ...newCases[caseIndex] };
      
      const updateItem = (items: ChecklistItem[]): boolean => {
        for (const item of items) {
          if (item.id === itemId) {
            item.completionPercentage = percentage;
            item.isComplete = percentage === 100;
            
            // If this is a linked item, update parent completion
            if (item.linkedChecklistId) {
              get().updateParentCompletion(caseId, itemId);
            }
            
            return true;
          }
          if (updateItem(item.children)) return true;
        }
        return false;
      };

      updateItem(targetCase.items);
      newCases[caseIndex] = targetCase;
      return { cases: newCases };
    });
  },

  getLinkedChecklistProgress: (caseId, itemId) => {
    const targetCase = get().cases.find(c => c.id === caseId);
    if (!targetCase) return 0;

    const findItem = (items: ChecklistItem[]): ChecklistItem | null => {
      for (const item of items) {
        if (item.id === itemId) return item;
        const found = findItem(item.children);
        if (found) return found;
      }
      return null;
    };

    const item = findItem(targetCase.items);
    return item?.completionPercentage || 0;
  },
  
  createSubChecklist: (parentCaseId, parentItemId, items) => {
    console.log('Creating sub-checklist for parent case:', parentCaseId);
    console.log('Parent item ID:', parentItemId);
    console.log('Items to include:', items.map(item => ({ id: item.id, title: item.title })));
    
    const parentCase = get().cases.find(c => c.id === parentCaseId);
    if (!parentCase) {
      console.error('Parent case not found:', parentCaseId);
      return null;
    }
    
    const parentItem = findItemInCase(parentCase, parentItemId);
    if (!parentItem) {
      console.error('Parent item not found:', parentItemId);
      return null;
    }
    
    if (!parentItem.hasSubChecklist) {
      console.error('Parent item does not have sub-checklist flag:', parentItem.title);
      return null;
    }
    
    const subChecklistId = crypto.randomUUID();
    const subChecklistName = `${parentCase.name} - ${parentItem.title}`;
    
    console.log(`Creating sub-checklist: ${subChecklistName} (${subChecklistId})`);
    
    const newCase: Case = {
      id: subChecklistId,
      name: subChecklistName,
      templateId: parentCase.templateId,
      items: JSON.parse(JSON.stringify(items)),
      createdAt: new Date(),
      updatedAt: new Date(),
    };
    
    set(state => {
      // Add the new case
      const newCases = [...state.cases, newCase];
      
      // Update the parent item's linkedChecklistId
      const updatedCases = newCases.map(c => {
        if (c.id === parentCaseId) {
          const updatedCase = { ...c };
          const updateItem = (items: ChecklistItem[]): boolean => {
            for (const item of items) {
              if (item.id === parentItemId) {
                item.linkedChecklistId = subChecklistId;
                console.log(`Updated parent item ${item.title} with linkedChecklistId: ${subChecklistId}`);
                return true;
              }
              if (updateItem(item.children)) return true;
            }
            return false;
          };
          updateItem(updatedCase.items);
          return updatedCase;
        }
        return c;
      });
      
      return { cases: updatedCases };
    });
    
    return subChecklistId;
  },
  
  updateParentCompletion: (caseId, itemId) => {
    console.log('Updating parent completion for case:', caseId);
    console.log('Item ID:', itemId);
    
    set(state => {
      const caseIndex = state.cases.findIndex(c => c.id === caseId);
      if (caseIndex === -1) {
        console.error('Case not found:', caseId);
        return state;
      }
      
      const newCases = [...state.cases];
      const targetCase = { ...newCases[caseIndex] };
      
      // Find the parent item that contains this item
      const findParentItem = (items: ChecklistItem[], targetId: string): ChecklistItem | null => {
        for (const item of items) {
          // Check if this item has the target as a child
          if (item.children.some(child => child.id === targetId)) {
            console.log('Found parent item:', item.title);
            return item;
          }
          
          // Recursively search children
          const found = findParentItem(item.children, targetId);
          if (found) return found;
        }
        return null;
      };
      
      // Find the updated item
      const findItem = (items: ChecklistItem[]): ChecklistItem | null => {
        for (const item of items) {
          if (item.id === itemId) {
            console.log('Found updated item:', item.title);
            return item;
          }
          const found = findItem(item.children);
          if (found) return found;
        }
        return null;
      };
      
      const updatedItem = findItem(targetCase.items);
      if (!updatedItem) {
        console.error('Updated item not found:', itemId);
        return state;
      }
      
      const parentItem = findParentItem(targetCase.items, itemId);
      if (!parentItem) {
        console.log('No parent item found for:', itemId);
        return state;
      }
      
      // Check if all children are complete
      const allChildrenComplete = parentItem.children.every(child => child.isComplete);
      console.log('All children complete:', allChildrenComplete);
      
      // Update parent completion status
      if (parentItem.isComplete !== allChildrenComplete) {
        console.log('Updating parent completion from', parentItem.isComplete, 'to', allChildrenComplete);
        parentItem.isComplete = allChildrenComplete;
        
        // If this parent has a parent, update that too
        if (parentItem.id !== targetCase.items[0].id) {
          // Use a flag to prevent infinite recursion
          const parentId = parentItem.id;
          setTimeout(() => {
            get().updateParentCompletion(caseId, parentId);
          }, 0);
        }
      }
      
      newCases[caseIndex] = targetCase;
      return { cases: newCases };
    });
  },
  
  refreshChecklistCompletion: (caseId) => {
    console.log('Refreshing checklist completion for case:', caseId);
    
    set(state => {
      const caseIndex = state.cases.findIndex(c => c.id === caseId);
      if (caseIndex === -1) {
        console.error('Case not found:', caseId);
        return state;
      }
      
      const newCases = [...state.cases];
      const targetCase = { ...newCases[caseIndex] };
      
      // Track which items have been updated to prevent infinite loops
      const updatedItems = new Set<string>();
      
      // Recursively check and update completion status
      const checkChildrenCompletion = (items: ChecklistItem[]): void => {
        for (const item of items) {
          // Skip items without children
          if (!item.children || item.children.length === 0) continue;
          
          // Check if all children are complete
          const allChildrenComplete = item.children.every(child => child.isComplete);
          console.log(`Item ${item.title}: all children complete = ${allChildrenComplete}`);
          
          // Update completion status if needed
          if (item.isComplete !== allChildrenComplete) {
            console.log(`Updating ${item.title} completion from ${item.isComplete} to ${allChildrenComplete}`);
            item.isComplete = allChildrenComplete;
            updatedItems.add(item.id);
          }
          
          // Recursively check children
          checkChildrenCompletion(item.children);
        }
      };
      
      checkChildrenCompletion(targetCase.items);
      
      // Only update the state if changes were made
      if (updatedItems.size > 0) {
        console.log(`Updated ${updatedItems.size} items in checklist ${caseId}`);
        newCases[caseIndex] = targetCase;
        return { cases: newCases };
      }
      
      return state;
    });
  }
}));

// Helper function to find an item in a case
const findItemInCase = (case_: Case, itemId: string): ChecklistItem | null => {
  const findItem = (items: ChecklistItem[]): ChecklistItem | null => {
    for (const item of items) {
      if (item.id === itemId) return item;
      const found = findItem(item.children);
      if (found) return found;
    }
    return null;
  };
  
  return findItem(case_.items);
}; 