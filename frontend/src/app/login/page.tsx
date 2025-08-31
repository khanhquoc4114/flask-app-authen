"use client";

import React, { useState, useEffect } from 'react';
import { 
  Form, 
  Input, 
  Button, 
  Checkbox, 
  Typography, 
  Space, 
  Divider, 
  message, 
  Card,
  Row,
  Col,
  Alert
} from 'antd';
import { 
  UserOutlined, 
  LockOutlined, 
  GoogleOutlined, 
  GithubOutlined,
  LoginOutlined,
  EyeInvisibleOutlined,
  EyeTwoTone
} from '@ant-design/icons';
import { useRouter } from 'next/navigation';
import axios from 'axios';

const { Title, Text, Link } = Typography;

interface LoginFormValues {
  email: string;
  password: string;
  remember?: boolean;
}

interface LoginResponse {
  access_token: string;
  token_type: string;
}

interface SocialLoginResponse {
  url: string; // URL để redirect đến OAuth provider
}

const LoginForm: React.FC = () => {
  const [form] = Form.useForm();
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [socialLoading, setSocialLoading] = useState<{
    google: boolean;
    github: boolean;
  }>({
    google: false,
    github: false
  });

const getAPIUrl = () => {
  // Trong development với Docker
  if (typeof window !== 'undefined') {
    // Browser context - cần localhost để OAuth work
    return process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  }
  // Server context - có thể dùng internal network
  return process.env.NEXT_PUBLIC_API_URL || 'http://backend:8000';
};

  useEffect(() => {
    // Query string
    const params = new URLSearchParams(window.location.search);
    const token = params.get("token");

    if (token) {
      localStorage.setItem("access_token", token);

      // Redirect sang dashboard
      router.push("/dashboard");

    }
  });

  // Xử lý đăng nhập thông thường
const onFinish = async (values: LoginFormValues) => {
  setLoading(true);
  
  try {
    const response = await axios.post<LoginResponse>(
      `${process.env.NEXT_PUBLIC_API_URL}/api/auth/login`,
      {
        email: values.email,
        password: values.password,
      }
    );
    // ... rest of the code
  } catch (error) {
    // ... error handling
  } finally {
    setLoading(false);
  }
};

const getOAuthURL = () => {
  return process.env.NEXT_PUBLIC_OAUTH_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
};

  // Xử lý đăng nhập bằng Google
const handleGoogleLogin = async () => {
  setSocialLoading(prev => ({ ...prev, google: true }));
  
  try {
    // Sử dụng OAuth-specific URL
    window.location.href = `${getOAuthURL()}/auth/google`;
  } catch (error) {
    console.error("Google login error:", error);
    message.error("Không thể kết nối với Google. Vui lòng thử lại!");
  } finally {
    setSocialLoading(prev => ({ ...prev, google: false }));
  }
};

  // Xử lý đăng nhập bằng GitHub
const handleGithubLogin = async () => {
  setSocialLoading(prev => ({ ...prev, github: true }));
  
  try {
    window.location.href = `${getOAuthURL()}/auth/github`;
  } catch (error) {
    console.error("GitHub login error:", error);
    message.error("Không thể kết nối với GitHub. Vui lòng thử lại!");
  } finally {
    setSocialLoading(prev => ({ ...prev, github: false }));
  }
};

  // Xử lý quên mật khẩu
  const handleForgotPassword = () => {
    router.push("/forgot-password");
  };

  // Validation rules
  const emailRules = [
    { required: true, message: 'Vui lòng nhập email!' },
    { type: 'email' as const, message: 'Email không hợp lệ!' }
  ];

  const passwordRules = [
    { required: true, message: 'Vui lòng nhập mật khẩu!' },
    { min: 6, message: 'Mật khẩu phải có ít nhất 6 ký tự!' }
  ];

  return (
    <div style={{ 
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      padding: '20px'
    }}>
      <Card
        style={{
          width: '100%',
          maxWidth: 450,
          borderRadius: 12,
          boxShadow: '0 8px 32px rgba(0,0,0,0.1)',
          border: 'none'
        }}
        styles={{
          body: { padding: '40px' }
        }}
      >
        {/* Header */}
        <Space direction="vertical" size="large" style={{ width: '100%', textAlign: 'center' }}>
          <div>
            <div style={{
              width: 80,
              height: 80,
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 20px',
              boxShadow: '0 4px 16px rgba(102, 126, 234, 0.3)'
            }}>
              <LoginOutlined style={{ fontSize: 32, color: 'white' }} />
            </div>
            <Title level={2} style={{ margin: '0 0 8px 0', color: '#262626' }}>
              Đăng nhập
            </Title>
            <Text type="secondary">Chào mừng bạn quay trở lại</Text>
          </div>

          {/* Login Form */}
          <Form
            form={form}
            name="login"
            size="large"
            onFinish={onFinish}
            autoComplete="off"
            layout="vertical"
            style={{ width: '100%' }}
          >
            <Form.Item
              label="Email"
              name="email"
              rules={emailRules}
              style={{ marginBottom: 20 }}
            >
              <Input
                prefix={<UserOutlined style={{ color: '#bfbfbf' }} />}
                placeholder="Nhập email của bạn"
                autoComplete="email"
              />
            </Form.Item>

            <Form.Item
              label="Mật khẩu"
              name="password"
              rules={passwordRules}
              style={{ marginBottom: 16 }}
            >
              <Input.Password
                prefix={<LockOutlined style={{ color: '#bfbfbf' }} />}
                placeholder="Nhập mật khẩu của bạn"
                autoComplete="current-password"
                iconRender={(visible) => (visible ? <EyeTwoTone /> : <EyeInvisibleOutlined />)}
              />
            </Form.Item>

            <Row justify="space-between" align="middle" style={{ marginBottom: 24 }}>
              <Col>
                <Form.Item name="remember" valuePropName="checked" style={{ margin: 0 }}>
                  <Checkbox>Ghi nhớ đăng nhập</Checkbox>
                </Form.Item>
              </Col>
              <Col>
                <Link onClick={handleForgotPassword} style={{ fontSize: 14 }}>
                  Quên mật khẩu?
                </Link>
              </Col>
            </Row>

            <Form.Item style={{ marginBottom: 16 }}>
              <Button
                type="primary"
                htmlType="submit"
                loading={loading}
                block
                style={{
                  height: 45,
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  border: 'none',
                  borderRadius: 8,
                  fontWeight: 500
                }}
                icon={<LoginOutlined />}
              >
                {loading ? 'Đang xử lý...' : 'Đăng nhập'}
              </Button>
            </Form.Item>
          </Form>

          {/* Divider */}
          <Divider style={{ margin: '20px 0', color: '#bfbfbf', fontSize: 14 }}>
            Hoặc đăng nhập bằng
          </Divider>

          {/* Social Login Buttons */}
          <Space direction="vertical" size="middle" style={{ width: '100%' }}>
            <Button
              icon={<GoogleOutlined />}
              onClick={handleGoogleLogin}
              loading={socialLoading.google}
              block
              size="large"
              style={{
                height: 45,
                borderColor: '#db4437',
                color: '#db4437',
                borderRadius: 8,
                fontWeight: 500
              }}
            >
              {socialLoading.google ? 'Đang kết nối...' : 'Đăng nhập với Google'}
            </Button>

            <Button
              icon={<GithubOutlined />}
              onClick={handleGithubLogin}
              loading={socialLoading.github}
              block
              size="large"
              style={{
                height: 45,
                borderColor: '#333',
                color: '#333',
                borderRadius: 8,
                fontWeight: 500
              }}
            >
              {socialLoading.github ? 'Đang kết nối...' : 'Đăng nhập với GitHub'}
            </Button>
          </Space>

          {/* Register Link */}
          <Text style={{ textAlign: 'center', marginTop: 20 }}>
            Chưa có tài khoản?{' '}
            <Link 
              onClick={() => router.push('/register')}
              style={{ fontWeight: 500 }}
            >
              Đăng ký ngay
            </Link>
          </Text>
        </Space>
      </Card>
    </div>
  );
};

export default LoginForm;