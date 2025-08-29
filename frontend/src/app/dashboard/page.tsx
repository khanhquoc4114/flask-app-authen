"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { 
  Layout, 
  Typography, 
  Card, 
  Button, 
  message, 
  Spin, 
  Avatar,
  Tag,
  Row,
  Col,
  Divider,
  Space
} from "antd";
import {
  UserOutlined,
  LogoutOutlined,
  MailOutlined,
  CalendarOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  EditOutlined
} from '@ant-design/icons';
import api from "@/utils/api";

const { Header, Content } = Layout;
const { Title, Text } = Typography;

interface User {
  id: number;
  email: string;
  full_name: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export default function Dashboard() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchUser() {
      try {
        const { data } = await api.get<User>("/api/auth/user", {
            headers: {
              Authorization: `Bearer ${localStorage.getItem("access_token")}`
            }
        });
        setUser(data);
      } catch (err) {
        console.error(err);
        message.error("Không thể tải thông tin người dùng");
        localStorage.removeItem("access_token");
        localStorage.removeItem("token_type");
        router.push("/login");
      } finally {
        setLoading(false);
      }
    }
    fetchUser();
  }, [router]);

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("token_type");
    message.success("Đăng xuất thành công!");
    router.push("/login");
  };

  if (loading) {
    return (
      <div style={{ 
        height: '100vh', 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
      }}>
        <Card style={{ textAlign: 'center', borderRadius: '12px', boxShadow: '0 8px 32px rgba(0,0,0,0.1)' }}>
          <Spin size="large" />
          <div style={{ marginTop: '16px', color: '#666' }}>Đang tải...</div>
        </Card>
      </div>
    );
  }

  if (!user) return null;

  const getInitials = (name: string) => {
    return name.split(' ').map(word => word[0]).join('').toUpperCase();
  };

  return (
    <Layout style={{ minHeight: "100vh", background: '#f0f2f5' }}>
      {/* Header với gradient */}
      <Header style={{ 
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        padding: '0 24px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <Title level={3} style={{ color: '#fff', margin: 0 }}>
          Dashboard
        </Title>
        <Button 
          type="text" 
          icon={<LogoutOutlined />}
          onClick={handleLogout}
          style={{ color: '#fff', border: '1px solid rgba(255,255,255,0.3)' }}
        >
          Đăng xuất
        </Button>
      </Header>

      <Content style={{ padding: "24px", maxWidth: '1200px', margin: '0 auto', width: '100%' }}>
        {/* Welcome Section */}
        <Card 
          style={{ 
            marginBottom: '24px',
            borderRadius: '16px',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            border: 'none',
            boxShadow: '0 8px 32px rgba(102, 126, 234, 0.3)'
          }}
        >
          <Row align="middle" gutter={24}>
            <Col>
              <Avatar 
                size={80} 
                style={{ 
                  backgroundColor: 'rgba(255,255,255,0.2)', 
                  color: '#fff',
                  fontSize: '24px',
                  fontWeight: 'bold'
                }}
                icon={user.full_name ? undefined : <UserOutlined />}
              >
                {user.full_name ? getInitials(user.full_name) : undefined}
              </Avatar>
            </Col>
            <Col flex={1}>
              <Title level={2} style={{ color: '#fff', margin: 0 }}>
                Xin chào, {user.full_name || user.email}! 👋
              </Title>
              <Text style={{ color: 'rgba(255,255,255,0.8)', fontSize: '16px' }}>
                Chào mừng bạn quay trở lại dashboard
              </Text>
            </Col>
          </Row>
        </Card>

        {/* User Info Cards */}
        <Row gutter={[24, 24]}>
          {/* Profile Card */}
          <Col xs={24} lg={16}>
            <Card
              title={
                <Space>
                  <UserOutlined style={{ color: '#667eea' }} />
                  <span>Thông tin cá nhân</span>
                </Space>
              }
              extra={<Button type="link" icon={<EditOutlined />}>Chỉnh sửa</Button>}
              style={{ 
                borderRadius: '12px',
                boxShadow: '0 4px 16px rgba(0,0,0,0.06)'
              }}
            >
              <Row gutter={[0, 16]}>
                <Col span={24}>
                  <div style={{ display: 'flex', alignItems: 'center', marginBottom: '12px' }}>
                    <MailOutlined style={{ color: '#667eea', marginRight: '8px' }} />
                    <Text strong>Email: </Text>
                    <Text style={{ marginLeft: '8px' }}>{user.email}</Text>
                  </div>
                </Col>
                <Col span={24}>
                  <div style={{ display: 'flex', alignItems: 'center', marginBottom: '12px' }}>
                    <UserOutlined style={{ color: '#667eea', marginRight: '8px' }} />
                    <Text strong>Họ tên: </Text>
                    <Text style={{ marginLeft: '8px' }}>{user.full_name || "Chưa cập nhật"}</Text>
                  </div>
                </Col>
                <Col span={24}>
                  <div style={{ display: 'flex', alignItems: 'center', marginBottom: '12px' }}>
                    <Text strong>ID: </Text>
                    <Tag color="blue" style={{ marginLeft: '8px' }}>{user.id}</Tag>
                  </div>
                </Col>
                <Col span={24}>
                  <div style={{ display: 'flex', alignItems: 'center' }}>
                    <Text strong>Trạng thái: </Text>
                    <Tag 
                      color={user.is_active ? "success" : "error"}
                      icon={user.is_active ? <CheckCircleOutlined /> : <CloseCircleOutlined />}
                      style={{ marginLeft: '8px' }}
                    >
                      {user.is_active ? "Hoạt động" : "Không hoạt động"}
                    </Tag>
                  </div>
                </Col>
              </Row>
            </Card>
          </Col>

          {/* Activity Card */}
          <Col xs={24} lg={8}>
            <Card
              title={
                <Space>
                  <CalendarOutlined style={{ color: '#52c41a' }} />
                  <span>Hoạt động</span>
                </Space>
              }
              style={{ 
                borderRadius: '12px',
                boxShadow: '0 4px 16px rgba(0,0,0,0.06)',
                height: '100%'
              }}
            >
              <div style={{ marginBottom: '16px' }}>
                <Text strong style={{ color: '#52c41a' }}>Ngày tạo tài khoản</Text>
                <div style={{ marginTop: '8px' }}>
                  <Text>{new Date(user.created_at).toLocaleDateString('vi-VN')}</Text>
                </div>
                <div style={{ fontSize: '12px', color: '#999', marginTop: '4px' }}>
                  {new Date(user.created_at).toLocaleTimeString('vi-VN')}
                </div>
              </div>
              
              <Divider style={{ margin: '16px 0' }} />
              
              <div>
                <Text strong style={{ color: '#1890ff' }}>Cập nhật lần cuối</Text>
                <div style={{ marginTop: '8px' }}>
                  <Text>{new Date(user.updated_at).toLocaleDateString('vi-VN')}</Text>
                </div>
                <div style={{ fontSize: '12px', color: '#999', marginTop: '4px' }}>
                  {new Date(user.updated_at).toLocaleTimeString('vi-VN')}
                </div>
              </div>
            </Card>
          </Col>
        </Row>

        {/* Quick Actions */}
        <Card 
          title="Hành động nhanh"
          style={{ 
            marginTop: '24px',
            borderRadius: '12px',
            boxShadow: '0 4px 16px rgba(0,0,0,0.06)'
          }}
        >
          <Row gutter={16}>
            <Col>
              <Button type="primary" size="large" icon={<EditOutlined />}>
                Chỉnh sửa hồ sơ
              </Button>
            </Col>
            <Col>
              <Button size="large">
                Đổi mật khẩu
              </Button>
            </Col>
            <Col>
              <Button size="large">
                Cài đặt
              </Button>
            </Col>
          </Row>
        </Card>
      </Content>
    </Layout>
  );
}