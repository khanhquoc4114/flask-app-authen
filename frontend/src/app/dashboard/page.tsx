"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Layout, Typography, Descriptions, Button, message, Spin } from "antd";
import api from "@/utils/api";

const { Header, Content, Footer } = Layout;
const { Title } = Typography;

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
          withCredentials: true,
        });
        setUser(data);
      } catch (err) {
        console.error(err);
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
    router.push("/login");
  };

  if (loading) return <Spin size="large" />;

  if (!user) return null;

  return (
    <Layout style={{ minHeight: "100vh" }}>
      <Header style={{ color: "#fff", fontSize: 20 }}>Dashboard</Header>
      <Content style={{ padding: "50px" }}>
        <Title level={2}>Welcome, {user.full_name || user.email}</Title>
        <Descriptions bordered column={1} style={{ marginTop: 20 }}>
          <Descriptions.Item label="ID">{user.id}</Descriptions.Item>
          <Descriptions.Item label="Email">{user.email}</Descriptions.Item>
          <Descriptions.Item label="Full Name">{user.full_name || "-"}</Descriptions.Item>
          <Descriptions.Item label="Active">{user.is_active ? "Yes" : "No"}</Descriptions.Item>
          <Descriptions.Item label="Created At">{new Date(user.created_at).toLocaleString()}</Descriptions.Item>
          <Descriptions.Item label="Updated At">{new Date(user.updated_at).toLocaleString()}</Descriptions.Item>
        </Descriptions>
        <Button type="primary" danger style={{ marginTop: 20 }} onClick={handleLogout}>
          Logout
        </Button>
      </Content>
      <Footer style={{ textAlign: "center" }}>© 2025 My App</Footer>
    </Layout>
  );
}
