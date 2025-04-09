export type ChecklistItem = {
  id: string;
  title: string;
  description?: string;
  isComplete: boolean;
  children: ChecklistItem[];
  dependencies: string[]; // IDs of items this depends on
  dependents: string[]; // IDs of items that depend on this
  linkedChecklistId?: string; // ID of another checklist this item links to
  completionPercentage?: number; // Percentage of linked checklist completion
  templateId?: string;
  level: number; // Indentation level (0-based)
  hasSubChecklist: boolean; // Whether this item has its own checklist
};

export type CaseTemplate = {
  id: string;
  name: string;
  description: string;
  rootItems: ChecklistItem[];
  sourceText?: string; // Original plain text input
};

export type Case = {
  id: string;
  name: string;
  templateId: string;
  items: ChecklistItem[];
  createdAt: Date;
  updatedAt: Date;
}; 