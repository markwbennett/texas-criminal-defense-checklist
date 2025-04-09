import { useEffect, useState } from 'react'
import { Container, Box, Typography, Button, Paper, Tabs, Tab } from '@mui/material'
import { useChecklistStore } from './store/checklistStore'
import { CaseView } from './components/CaseView'
import { ChecklistNavigation } from './components/ChecklistNavigation'
import { CreateChecklistButton } from './components/CreateChecklistButton'
import { TextChecklistInput } from './components/TextChecklistInput'
import { CaseTemplate } from './types/checklist'
import { useParams, useNavigate } from 'react-router-dom'

const sampleTemplate: CaseTemplate = {
  id: 'template1',
  name: 'Drug Possession Defense',
  description: 'Template for drug possession cases',
  rootItems: [
    {
      id: 'item1',
      title: 'Initial Client Meeting',
      description: 'First meeting with client to gather basic information',
      isComplete: false,
      children: [
        {
          id: 'item1.1',
          title: 'Client Personal Information',
          isComplete: false,
          children: [],
          dependencies: [],
          dependents: ['item2.1'],
          level: 1,
          hasSubChecklist: false
        }
      ],
      dependencies: [],
      dependents: [],
      level: 0,
      hasSubChecklist: true
    },
    {
      id: 'item2',
      title: 'Evidence Review',
      isComplete: false,
      children: [
        {
          id: 'item2.1',
          title: 'Police Report Analysis',
          description: 'Review and analyze police report',
          isComplete: false,
          children: [],
          dependencies: ['item1.1'],
          dependents: [],
          level: 1,
          hasSubChecklist: false
        }
      ],
      dependencies: [],
      dependents: [],
      level: 0,
      hasSubChecklist: true
    },
    {
      id: 'item3',
      title: 'Complete Discovery Checklist',
      description: 'Review all discovery materials',
      isComplete: false,
      children: [],
      dependencies: [],
      dependents: [],
      linkedChecklistId: 'discovery-checklist',
      completionPercentage: 0,
      level: 0,
      hasSubChecklist: true
    }
  ]
}

const discoveryTemplate: CaseTemplate = {
  id: 'discovery-checklist',
  name: 'Discovery Review',
  description: 'Checklist for reviewing discovery materials',
  rootItems: [
    {
      id: 'd1',
      title: 'Police Reports',
      isComplete: false,
      children: [],
      dependencies: [],
      dependents: [],
      level: 0,
      hasSubChecklist: false
    },
    {
      id: 'd2',
      title: 'Lab Reports',
      isComplete: false,
      children: [],
      dependencies: [],
      dependents: [],
      level: 0,
      hasSubChecklist: false
    },
    {
      id: 'd3',
      title: 'Witness Statements',
      isComplete: false,
      children: [],
      dependencies: [],
      dependents: [],
      level: 0,
      hasSubChecklist: false
    },
    {
      id: 'd4',
      title: 'Video Evidence',
      isComplete: false,
      children: [],
      dependencies: [],
      dependents: [],
      level: 0,
      hasSubChecklist: false
    }
  ]
}

function App() {
  const { templates, cases, addCase, updateLinkedChecklistProgress, refreshChecklistCompletion } = useChecklistStore()
  const [currentCaseId, setCurrentCaseId] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState(0)
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  
  useEffect(() => {
    console.log('App mounted, templates:', templates, 'cases:', cases)
    if (templates.length === 0) {
      console.log('Setting up initial templates and cases')
      useChecklistStore.setState({ templates: [sampleTemplate, discoveryTemplate] })
      
      // Create main case
      const mainCaseId = addCase('template1', 'State v. Smith')
      
      // Create discovery case
      const discoveryCaseId = addCase('discovery-checklist', 'Discovery Review - State v. Smith')
      
      if (mainCaseId && discoveryCaseId) {
        setCurrentCaseId(mainCaseId)
        
        // Find the main case and update the linkedChecklistId for the "Complete Discovery Checklist" item
        const mainCase = cases.find(c => c.id === mainCaseId);
        if (mainCase) {
          const discoveryItem = mainCase.items.find(item => item.title === 'Complete Discovery Checklist');
          if (discoveryItem) {
            discoveryItem.linkedChecklistId = discoveryCaseId;
          }
        }
        
        // Create sub-checklists for the other items with hasSubChecklist=true
        const mainCase2 = cases.find(c => c.id === mainCaseId);
        if (mainCase2) {
          mainCase2.items.forEach(item => {
            if (item.hasSubChecklist && !item.linkedChecklistId && item.children.length > 0) {
              // Create a sub-checklist for this item
              const subChecklistId = useChecklistStore.getState().createSubChecklist(
                mainCaseId, 
                item.id, 
                item.children
              );
              
              if (subChecklistId) {
                console.log(`Created sub-checklist for ${item.title}: ${subChecklistId}`);
              }
            }
          });
        }
        
        // Simulate progress on the discovery checklist
        setTimeout(() => {
          // Complete 2 out of 4 items (50%)
          updateLinkedChecklistProgress(discoveryCaseId, 'd1', 100)
          updateLinkedChecklistProgress(discoveryCaseId, 'd2', 100)
          
          // Update the linked item in the main case
          updateLinkedChecklistProgress(mainCaseId, 'item3', 50)
        }, 1000)
      }
    }
  }, [templates.length, addCase, updateLinkedChecklistProgress, cases])
  
  // Handle route changes
  useEffect(() => {
    if (id) {
      console.log('Route changed to checklist ID:', id);
      console.log('Available cases:', cases.map(c => ({ id: c.id, name: c.name })));
      
      // Check if this is a valid checklist ID
      const checklist = cases.find(c => c.id === id);
      if (checklist) {
        console.log('Found checklist:', checklist.name);
        console.log('Checklist items:', checklist.items.map(item => ({
          id: item.id,
          title: item.title,
          isComplete: item.isComplete,
          hasSubChecklist: item.hasSubChecklist,
          linkedChecklistId: item.linkedChecklistId
        })));
        
        // Only update state if the current case ID is different
        if (currentCaseId !== id) {
          setCurrentCaseId(id);
          setActiveTab(0); // Switch to the Checklists tab
        }
        
        // Refresh completion status when navigating to a checklist
        refreshChecklistCompletion(id);
      } else {
        console.log('Checklist not found, navigating to home');
        // If not found, navigate back to home
        navigate('/');
      }
    }
  }, [id, cases, navigate, refreshChecklistCompletion, currentCaseId]);

  const handleCaseChange = (caseId: string) => {
    setCurrentCaseId(caseId)
    navigate(`/checklist/${caseId}`);
  }

  const handleTabChange = (_: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue)
  }

  const currentCase = cases.find(c => c.id === currentCaseId)

  if (cases.length === 0) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Typography>Loading cases...</Typography>
      </Container>
    )
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Paper sx={{ p: 3, mb: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h5">Criminal Defense Checklists</Typography>
          <CreateChecklistButton templates={templates} />
        </Box>
        
        <Tabs value={activeTab} onChange={handleTabChange} sx={{ mb: 2 }}>
          <Tab label="Checklists" />
          <Tab label="Create from Text" />
        </Tabs>
        
        {activeTab === 0 ? (
          <>
            <ChecklistNavigation 
              cases={cases} 
              currentCaseId={currentCaseId} 
              onCaseChange={handleCaseChange} 
            />
            
            {currentCase ? (
              <CaseView case={currentCase} />
            ) : (
              <Typography>Select a checklist to view</Typography>
            )}
          </>
        ) : (
          <TextChecklistInput />
        )}
      </Paper>
    </Container>
  )
}

export default App
