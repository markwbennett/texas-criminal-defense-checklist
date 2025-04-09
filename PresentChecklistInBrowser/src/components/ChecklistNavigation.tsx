import { Box, Tabs, Tab, Typography } from '@mui/material';
import { Case } from '../types/checklist';

interface Props {
  cases: Case[];
  currentCaseId: string | null;
  onCaseChange: (caseId: string) => void;
}

export const ChecklistNavigation = ({ cases, currentCaseId, onCaseChange }: Props) => {
  const handleChange = (_: React.SyntheticEvent, newValue: string) => {
    onCaseChange(newValue);
  };

  return (
    <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
      <Tabs 
        value={currentCaseId || ''} 
        onChange={handleChange}
        aria-label="checklist tabs"
      >
        {cases.map((caseItem) => (
          <Tab 
            key={caseItem.id} 
            label={
              <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start' }}>
                <Typography variant="body1">{caseItem.name}</Typography>
                <Typography variant="caption" color="text.secondary">
                  {new Date(caseItem.createdAt).toLocaleDateString()}
                </Typography>
              </Box>
            } 
            value={caseItem.id} 
          />
        ))}
      </Tabs>
    </Box>
  );
}; 