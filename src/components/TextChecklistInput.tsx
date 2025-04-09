import { useState } from 'react';
import { Box, TextField, Button, Typography, Paper } from '@mui/material';
import { parseChecklistText } from '../utils/checklistParser';
import { useChecklistStore } from '../store/checklistStore';

export const TextChecklistInput = () => {
  const [checklistText, setChecklistText] = useState('');
  const [checklistName, setChecklistName] = useState('');
  const { templates, addCase } = useChecklistStore();
  
  const handleCreateChecklist = () => {
    if (!checklistText.trim() || !checklistName.trim()) return;
    
    // Parse the text into a template
    const template = parseChecklistText(checklistText, checklistName);
    
    // Add the template to the store
    useChecklistStore.setState(state => ({
      templates: [...state.templates, template]
    }));
    
    // Create a case from the template
    addCase(template.id, checklistName);
    
    // Reset the form
    setChecklistText('');
    setChecklistName('');
  };
  
  return (
    <Paper sx={{ p: 3, mb: 4 }}>
      <Typography variant="h6" gutterBottom>
        Create Checklist from Text
      </Typography>
      
      <TextField
        label="Checklist Name"
        fullWidth
        value={checklistName}
        onChange={(e) => setChecklistName(e.target.value)}
        sx={{ mb: 2 }}
      />
      
      <TextField
        label="Checklist Items (use indentation for hierarchy)"
        multiline
        rows={10}
        fullWidth
        value={checklistText}
        onChange={(e) => setChecklistText(e.target.value)}
        placeholder="Client intake
  Get client contact information
  Get contract signed
  Get paid
Gather records
  Request discovery
  Get initial discovery
  File HIPAA motion"
        sx={{ mb: 2, fontFamily: 'monospace' }}
      />
      
      <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
        <Button 
          variant="contained" 
          onClick={handleCreateChecklist}
          disabled={!checklistText.trim() || !checklistName.trim()}
        >
          Create Checklist
        </Button>
      </Box>
    </Paper>
  );
}; 