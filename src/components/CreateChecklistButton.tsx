import { useState } from 'react';
import { Button, Dialog, DialogTitle, DialogContent, DialogActions, TextField, MenuItem, Box, Typography } from '@mui/material';
import { CaseTemplate } from '../types/checklist';
import { useChecklistStore } from '../store/checklistStore';

interface Props {
  templates: CaseTemplate[];
}

export const CreateChecklistButton = ({ templates }: Props) => {
  const [open, setOpen] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState('');
  const [checklistName, setChecklistName] = useState('');
  const { addCase } = useChecklistStore();

  const handleOpen = () => {
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
    setSelectedTemplate('');
    setChecklistName('');
  };

  const handleCreate = () => {
    if (selectedTemplate && checklistName) {
      addCase(selectedTemplate, checklistName);
      handleClose();
    }
  };

  return (
    <>
      <Button variant="contained" color="primary" onClick={handleOpen}>
        Create New Checklist
      </Button>
      
      <Dialog open={open} onClose={handleClose}>
        <DialogTitle>Create New Checklist</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <TextField
              select
              label="Template"
              fullWidth
              value={selectedTemplate}
              onChange={(e) => setSelectedTemplate(e.target.value)}
              sx={{ mb: 2 }}
            >
              {templates.map((template) => (
                <MenuItem key={template.id} value={template.id}>
                  {template.name}
                </MenuItem>
              ))}
            </TextField>
            
            <TextField
              label="Checklist Name"
              fullWidth
              value={checklistName}
              onChange={(e) => setChecklistName(e.target.value)}
            />
            
            {selectedTemplate && (
              <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                {templates.find(t => t.id === selectedTemplate)?.description}
              </Typography>
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Cancel</Button>
          <Button 
            onClick={handleCreate} 
            variant="contained" 
            disabled={!selectedTemplate || !checklistName}
          >
            Create
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}; 