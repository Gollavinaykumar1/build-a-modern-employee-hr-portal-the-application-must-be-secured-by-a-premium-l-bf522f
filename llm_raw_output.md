# LLM Output

=== FILE: src/App.jsx ===
import React, { useState, useEffect, useCallback, useRef } from 'react';
import { HashRouter, Navigate, Route, Routes } from 'react-router-dom';
import axios from 'axios';
import { ToastContainer } from 'react-toastify';
import { toast } from 'react-toastify';
import { BiUser } from 'react-icons/bi';
import { AiOutlinePlus } from 'react-icons/ai';
import { MdOutlineWork } from 'react-icons/md';
import { FiCalendar } from 'react-icons/fi';
import { format } from 'date-fns';
import { useForm } from 'react-hook-form';
import { clsx } from 'clsx';
import 'react-toastify/dist/ReactToastify.css';

const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const App = () => {
  const [user, setUser] = useState(null);
  const [employees, setEmployees] = useState([]);
  const [openRoles, setOpenRoles] = useState(0);
  const [pendingLeaveRequests, setPendingLeaveRequests] = useState(0);
  const [period, setPeriod] = useState('week');
  const [recentRecords, setRecentRecords] = useState([]);
  const [showAddEmployeeModal, setShowAddEmployeeModal] = useState(false);
  const { register, handleSubmit, reset } = useForm();

  const fetchEmployees = useCallback(async () => {
    try {
      const response = await axios.get(`${BASE_URL}/employees`);
      const safeList = Array.isArray(response.data) ? response.data : (response.data?.items || []);
      setEmployees(safeList);
    } catch (error) {
      console.error(error);
    }
  }, []);

  const fetchOpenRoles = useCallback(async () => {
    try {
      const response = await axios.get(`${BASE_URL}/open-roles`);
      const safeList = Array.isArray(response.data) ? response.data : (response.data?.items || []);
      setOpenRoles(safeList.length);
    } catch (error) {
      console.error(error);
    }
  }, []);

  const fetchPendingLeaveRequests = useCallback(async () => {
    try {
      const response = await axios.get(`${BASE_URL}/pending-leave-requests`);
      const safeList = Array.isArray(response.data) ? response.data : (response.data?.items || []);
      setPendingLeaveRequests(safeList.length);
    } catch (error) {
      console.error(error);
    }
  }, []);

  const fetchRecentRecords = useCallback(async () => {
    try {
      const response = await axios.get(`${BASE_URL}/recent-records`);
      const safeList = Array.isArray(response.data) ? response.data : (response.data?.items || []);
      setRecentRecords(safeList);
    } catch (error) {
      console.error(error);
    }
  }, []);

  const handleLogin = useCallback(async (data) => {
    try {
      const response = await axios.post(`${BASE_URL}/login`, data);
      setUser(response.data);
    } catch (error) {
      console.error(error);
    }
  }, []);

  const handleRegister = useCallback(async (data) => {
    try {
      const response = await axios.post(`${BASE_URL}/register`, data);
      setUser(response.data);
    } catch (error) {
      console.error(error);
    }
  }, []);

  const handleAddEmployee = useCallback(async (data) => {
    try {
      const response = await axios.post(`${BASE_URL}/employees`, data);
      fetchEmployees();
      reset();
      setShowAddEmployeeModal(false);
    } catch (error) {
      console.error(error);
    }
  }, [fetchEmployees, reset]);

  useEffect(() => {
    fetchEmployees();
    fetchOpenRoles();
    fetchPendingLeaveRequests();
    fetchRecentRecords();
  }, [fetchEmployees, fetchOpenRoles, fetchPendingLeaveRequests, fetchRecentRecords]);

  if (!user) {
    return (
      <HashRouter>
        <Routes>
          <Route path="/login" element={
            <div className="h-screen flex justify-center items-center">
              <div className="bg-gray-800 p-4 rounded-lg shadow-lg">
                <h2 className="text-2xl text-white mb-4">Login</h2>
                <form onSubmit={handleSubmit(handleLogin)}>
                  <input type="email" placeholder="Email" className="block w-full p-2 mb-4 bg-gray-700 text-white" {...register('email')} />
                  <input type="password" placeholder="Password" className="block w-full p-2 mb-4 bg-gray-700 text-white" {...register('password')} />
                  <button type="submit" className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">Login</button>
                </form>
              </div>
            </div>
          } />
          <Route path="/register" element={
            <div className="h-screen flex justify-center items-center">
              <div className="bg-gray-800 p-4 rounded-lg shadow-lg">
                <h2 className="text-2xl text-white mb-4">Register</h2>
                <form onSubmit={handleSubmit(handleRegister)}>
                  <input type="text" placeholder="Name" className="block w-full p-2 mb-4 bg-gray-700 text-white" {...register('name')} />
                  <input type="email" placeholder="Email" className="block w-full p-2 mb-4 bg-gray-700 text-white" {...register('email')} />
                  <input type="password" placeholder="Password" className="block w-full p-2 mb-4 bg-gray-700 text-white" {...register('password')} />
                  <button type="submit" className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">Register</button>
                </form>
              </div>
            </div>
          } />
          <Route path="*" element={<Navigate to="/login" />} />
        </Routes>
      </HashRouter>
    );
  }

  return (
    <HashRouter>
      <div className="h-screen flex flex-col">
        <div className="bg-gray-800 p-4 flex justify-between items-center">
          <h1 className="text-2xl text-white">Employee HR Portal</h1>
          <button className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded" onClick={() => setUser(null)}>Logout</button>
        </div>
        <div className="flex-1 overflow-y-auto">
          <div className="p-4">
            <h2 className="text-2xl text-gray-700 mb-4">Dashboard</h2>
            <div className="grid grid-cols-3 gap-4 mb-4">
              <div className={clsx('bg-gray-700 p-4 rounded-lg shadow-lg', 'transition-all duration-300 hover:scale-105')}>
                <h3 className="text-lg text-white mb-2">Total Employees</h3>
                <p className="text-3xl text-white">{employees.length}</p>
              </div>
              <div className={clsx('bg-gray-700 p-4 rounded-lg shadow-lg', 'transition-all duration-300 hover:scale-105')}>
                <h3 className="text-lg text-white mb-2">Open Roles</h3>
                <p className="text-3xl text-white">{openRoles}</p>
              </div>
              <div className={clsx('bg-gray-700 p-4 rounded-lg shadow-lg', 'transition-all duration-300 hover:scale-105')}>
                <h3 className="text-lg text-white mb-2">Pending Leave Requests</h3>
                <p className="text-3xl text-white">{pendingLeaveRequests}</p>
              </div>
            </div>
            <div className="mb-4">
              <h2 className="text-2xl text-gray-700 mb-2">Employee Directory</h2>
              <table className="w-full text-gray-700">
                <thead>
                  <tr>
                    <th className="px-4 py-2">Name</th>
                    <th className="px-4 py-2">Department</th>
                    <th className="px-4 py-2">Role</th>
                    <th className="px-4 py-2">Employment Status</th>
                  </tr>
                </thead>
                <tbody>
                  {employees.map((employee) => (
                    <tr key={employee.id}>
                      <td className="px-4 py-2">{employee.name}</td>
                      <td className="px-4 py-2">{employee.department}</td>
                      <td className="px-4 py-2">{employee.role}</td>
                      <td className="px-4 py-2">
                        {employee.employmentStatus === 'active' ? (
                          <span className="bg-green-500 text-white py-1 px-2 rounded-lg">Active</span>
                        ) : employee.employmentStatus === 'onLeave' ? (
                          <span className="bg-yellow-500 text-white py-1 px-2 rounded-lg">On Leave</span>
                        ) : (
                          <span className="bg-red-500 text-white py-1 px-2 rounded-lg">Terminated</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="mb-4">
              <button className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded" onClick={() => setShowAddEmployeeModal(true)}>Add Employee</button>
            </div>
            {showAddEmployeeModal && (
              <div className="fixed top-0 left-0 w-full h-screen bg-gray-800 bg-opacity-50 flex justify-center items-center">
                <div className="bg-gray-700 p-4 rounded-lg shadow-lg">
                  <h2 className="text-2xl text-white mb-4">Add Employee</h2>
                  <form onSubmit={handleSubmit(handleAddEmployee)}>
                    <input type="text" placeholder="Name" className="block w-full p-2 mb-4 bg-gray-600 text-white" {...register('name')} />
                    <input type="email" placeholder="Email" className="block w-full p-2 mb-4 bg-gray-600 text-white" {...register('email')} />
                    <input type="text" placeholder="Department" className="block w-full p-2 mb-4 bg-gray-600 text-white" {...register('department')} />
                    <input type="text" placeholder="Role" className="block w-full p-2 mb-4 bg-gray-600 text-white" {...register('role')} />
                    <button type="submit" className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">Add Employee</button>
                  </form>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </HashRouter>
  );
};

export default App;
=== END ===