import React from 'react'
import { Box, Typography, Grid, Card, CardContent, Button, Chip } from '@mui/material'
import { 
  Assessment as AssessmentIcon,
  Upload as UploadIcon,
  PlayArrow as PlayIcon,
  Analytics as AnalyticsIcon,
  TrendingUp as TrendingUpIcon
} from '@mui/icons-material'

const Dashboard: React.FC = () => {
  return (
    <Box>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Resume-Based Interview System
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          AI-powered interview preparation with advanced analysis capabilities
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* Quick Actions */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Quick Actions
              </Typography>
              <Grid container spacing={2}>
                <Grid item>
                  <Button 
                    variant="contained" 
                    startIcon={<UploadIcon />}
                    href="/resume-upload"
                  >
                    Upload Resume
                  </Button>
                </Grid>
                <Grid item>
                  <Button 
                    variant="outlined" 
                    startIcon={<PlayIcon />}
                    href="/practice-mode"
                  >
                    Practice Mode
                  </Button>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* System Features */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                System Features
              </Typography>
              <Grid container spacing={1}>
                <Grid item>
                  <Chip 
                    icon={<AssessmentIcon />} 
                    label="NER-KE Algorithm v2.0" 
                    color="primary" 
                  />
                </Grid>
                <Grid item>
                  <Chip 
                    icon={<TrendingUpIcon />} 
                    label="FACS Vision Analysis" 
                    color="secondary" 
                  />
                </Grid>
                <Grid item>
                  <Chip 
                    icon={<AnalyticsIcon />} 
                    label="Voice Quality Engine" 
                    color="primary" 
                  />
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Activity */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent Activity
              </Typography>
              <Typography color="text.secondary">
                No recent activity. Start by uploading your resume to begin your interview preparation journey.
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  )
}

export default Dashboard