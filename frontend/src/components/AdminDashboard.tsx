import React, { useEffect, useState } from 'react'
import {
  Box,
  Heading,
  VStack,
  HStack,
  Text,
  Stat,
  StatLabel,
  StatNumber,
  SimpleGrid,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Card,
  CardHeader,
  CardBody,
  useColorModeValue,
  useToast,
  Badge,
  Spinner,
} from '@chakra-ui/react'
import { useAuth } from '../contexts/AuthContext'

type AdminMetrics = {
  total_users: number
  total_recordings: number
  recordings_last_7_days: number
}

export const AdminDashboard: React.FC = () => {
  const { user } = useAuth()
  const [metrics, setMetrics] = useState<AdminMetrics | null>(null)
  const [users, setUsers] = useState<any[]>([])
  const [recordings, setRecordings] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const toast = useToast()
  const cardBg = useColorModeValue('white', 'gray.800')
  const borderColor = useColorModeValue('gray.200', 'gray.700')

  useEffect(() => {
    if (!user?.is_admin) {
      setLoading(false)
      return
    }
    const token = localStorage.getItem('token')
    if (!token) {
      toast({ title: 'Not authenticated', status: 'error' })
      return
    }
    const headers = { 'Authorization': `Bearer ${token}` }
    Promise.all([
      fetch('/admin/metrics/summary', { headers }),
      fetch('/admin/users', { headers }),
      fetch('/admin/recordings?limit=25', { headers })
    ])
      .then(async ([m, u, r]) => {
        if (!m.ok || !u.ok || !r.ok) throw new Error('Admin fetch failed')
        setMetrics(await m.json())
        setUsers(await u.json())
        setRecordings(await r.json())
      })
      .catch(() => {
        toast({ title: 'Admin access required', status: 'error' })
      })
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <HStack justify="center" py={10}>
        <Spinner />
        <Text>Loading admin data...</Text>
      </HStack>
    )
  }

  if (!user?.is_admin) {
    return (
      <Box p={6} bg={cardBg} border="1px" borderColor={borderColor} borderRadius="lg">
        <Heading size="md" mb={2}>Admin access required</Heading>
        <Text>This area is only visible to admins. Ask an admin to enable your account.</Text>
      </Box>
    )
  }

  return (
    <VStack spacing={6} align="stretch">
      <Heading size="lg">Admin Dashboard</Heading>
      {metrics && (
        <SimpleGrid columns={{ base: 1, md: 3 }} spacing={4}>
          <Card bg={cardBg} border="1px" borderColor={borderColor}>
            <CardBody>
              <Stat>
                <StatLabel>Total Users</StatLabel>
                <StatNumber>{metrics.total_users}</StatNumber>
              </Stat>
            </CardBody>
          </Card>
          <Card bg={cardBg} border="1px" borderColor={borderColor}>
            <CardBody>
              <Stat>
                <StatLabel>Total Recordings</StatLabel>
                <StatNumber>{metrics.total_recordings}</StatNumber>
              </Stat>
            </CardBody>
          </Card>
          <Card bg={cardBg} border="1px" borderColor={borderColor}>
            <CardBody>
              <Stat>
                <StatLabel>Recordings (7 days)</StatLabel>
                <StatNumber>{metrics.recordings_last_7_days}</StatNumber>
              </Stat>
            </CardBody>
          </Card>
        </SimpleGrid>
      )}

      <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6}>
        <Card bg={cardBg} border="1px" borderColor={borderColor}>
          <CardHeader>
            <Heading size="md">Recent Users</Heading>
          </CardHeader>
          <CardBody>
            <Table size="sm">
              <Thead>
                <Tr>
                  <Th>Username</Th>
                  <Th>Email</Th>
                  <Th>Role</Th>
                </Tr>
              </Thead>
              <Tbody>
                {users.map(u => (
                  <Tr key={u._id}>
                    <Td>{u.username}</Td>
                    <Td>{u.email}</Td>
                    <Td>
                      <Badge colorScheme={u.is_admin ? 'purple' : 'gray'}>
                        {u.is_admin ? 'Admin' : 'User'}
                      </Badge>
                    </Td>
                  </Tr>
                ))}
              </Tbody>
            </Table>
          </CardBody>
        </Card>

        <Card bg={cardBg} border="1px" borderColor={borderColor}>
          <CardHeader>
            <Heading size="md">Recent Recordings</Heading>
          </CardHeader>
          <CardBody>
            <Table size="sm">
              <Thead>
                <Tr>
                  <Th>User</Th>
                  <Th>Session</Th>
                  <Th>Topic</Th>
                  <Th>Date</Th>
                </Tr>
              </Thead>
              <Tbody>
                {recordings.map((r: any) => (
                  <Tr key={r._id}>
                    <Td>{String(r.user_id)}</Td>
                    <Td>{r.session_type}</Td>
                    <Td>{r.topic}</Td>
                    <Td>{r.created_at ? new Date(r.created_at).toLocaleString() : ''}</Td>
                  </Tr>
                ))}
              </Tbody>
            </Table>
          </CardBody>
        </Card>
      </SimpleGrid>
    </VStack>
  )
}

export default AdminDashboard


