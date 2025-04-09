import React from 'react';
import { Box, Checkbox, Typography, Stack, LinearProgress, Button } from '@mui/material';
import { ChecklistItem as ChecklistItemType } from '../types/checklist';
import { useChecklistStore } from '../store/checklistStore';
import { useNavigate } from 'react-router-dom';

interface Props {
  item: ChecklistItemType;
  caseId: string;
  level?: number;
}

export const ChecklistItem = ({ item, caseId, level = 0 }: Props) => {
  const { toggleItem, getLinkedChecklistProgress, cases, createSubChecklist } = useChecklistStore();
  const navigate = useNavigate();
  const progress = item.linkedChecklistId ? getLinkedChecklistProgress(caseId, item.id) : undefined;

  const handleToggle = () => {
    console.log('Toggling item:', item.title);
    toggleItem(caseId, item.id);
  };

  const handleNavigateToSubChecklist = () => {
    console.log('Navigating to sub-checklist for:', item.title);
    console.log('Item has linkedChecklistId:', item.linkedChecklistId);
    console.log('Item hasSubChecklist:', item.hasSubChecklist);
    console.log('Available cases:', cases.map(c => ({ id: c.id, name: c.name })));
    
    if (item.linkedChecklistId) {
      console.log('Navigating to linked checklist:', item.linkedChecklistId);
      navigate(`/checklist/${item.linkedChecklistId}`);
      return;
    }
    
    if (item.hasSubChecklist) {
      // Try to find the sub-checklist by name
      const subChecklist = cases.find(c => c.name.includes(item.title));
      if (subChecklist) {
        console.log('Found sub-checklist by name:', subChecklist.name);
        navigate(`/checklist/${subChecklist.id}`);
        return;
      }
      
      // If not found, try to create one
      console.log('Creating new sub-checklist for:', item.title);
      const newChecklistId = createSubChecklist(caseId, item.id, item.children || []);
      if (newChecklistId) {
        console.log('Created new sub-checklist:', newChecklistId);
        navigate(`/checklist/${newChecklistId}`);
      } else {
        console.error('Failed to create sub-checklist');
      }
    }
  };

  return (
    <Box sx={{ ml: level * 2 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
        <Checkbox
          checked={item.isComplete}
          onChange={handleToggle}
          disabled={item.hasSubChecklist}
        />
        <Typography
          variant="body1"
          sx={{
            textDecoration: item.isComplete ? 'line-through' : 'none',
            cursor: item.hasSubChecklist ? 'pointer' : 'default',
            color: item.hasSubChecklist ? 'primary.main' : 'text.primary',
            '&:hover': item.hasSubChecklist ? { textDecoration: 'underline' } : {},
          }}
          onClick={item.hasSubChecklist ? handleNavigateToSubChecklist : undefined}
        >
          {item.title}
        </Typography>
      </Box>
      
      {item.description && (
        <Typography variant="body2" color="text.secondary" sx={{ ml: 1 }}>
          {item.description}
        </Typography>
      )}

      {item.linkedChecklistId && progress !== undefined && (
        <>
          <Typography component="span" variant="body2" color="text.secondary" sx={{ ml: 1 }}>
            ({progress}% complete)
          </Typography>
          <Box sx={{ mt: 1, width: '100%' }}>
            <LinearProgress 
              variant="determinate" 
              value={progress} 
              sx={{ height: 8, borderRadius: 4 }}
            />
          </Box>
        </>
      )}

      {/* Only show children if this is a sub-checklist view */}
      {item.children.length > 0 && level > 0 && (
        <Stack spacing={1} sx={{ mt: 1 }}>
          {item.children.map(child => (
            <ChecklistItem
              key={child.id}
              item={child}
              caseId={caseId}
              level={level + 1}
            />
          ))}
        </Stack>
      )}
    </Box>
  );
}; 