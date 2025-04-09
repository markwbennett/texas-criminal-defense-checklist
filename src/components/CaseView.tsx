import { Box, Typography, Stack } from '@mui/material';
import { Case } from '../types/checklist';
import { ChecklistItem } from './ChecklistItem';
import { useChecklistStore } from '../store/checklistStore';
import { useEffect } from 'react';

interface Props {
  case: Case;
}

export const CaseView = ({ case: checklistCase }: Props) => {
  const { refreshChecklistCompletion } = useChecklistStore();
  
  // Refresh completion status when checklist is loaded
  useEffect(() => {
    console.log('CaseView mounted for checklist:', checklistCase.id);
    console.log('Checklist name:', checklistCase.name);
    console.log('Checklist items:', checklistCase.items.map(item => ({
      id: item.id,
      title: item.title,
      isComplete: item.isComplete,
      hasSubChecklist: item.hasSubChecklist,
      linkedChecklistId: item.linkedChecklistId
    })));
    
    // Only refresh completion status when the checklist ID changes
    refreshChecklistCompletion(checklistCase.id);
  }, [checklistCase.id, refreshChecklistCompletion]);
  
  return (
    <Box sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>
        {checklistCase.name}
      </Typography>
      
      <Stack spacing={2}>
        {checklistCase.items.map(item => (
          <ChecklistItem 
            key={item.id} 
            item={item} 
            caseId={checklistCase.id} 
          />
        ))}
      </Stack>
    </Box>
  );
}; 