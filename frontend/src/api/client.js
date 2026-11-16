const API_BASE_URL = '/api/v1';

// Initial fallback mock data for standalone/Vercel static deployments
const DEFAULT_STORAGE = {
  batches: [
    { id: 1, name: 'Class 10 - Morning', subject: 'Maths & Science', timing: '7:00 AM - 9:00 AM', teacher_id: 2, teacher_name: 'Rahul Sharma', status: 'active' },
    { id: 2, name: 'Class 11 PCM - Evening', subject: 'Physics, Chemistry, Maths', timing: '4:00 PM - 6:00 PM', teacher_id: 2, teacher_name: 'Rahul Sharma', status: 'active' },
    { id: 3, name: 'Class 12 PCB - Morning', subject: 'Physics, Chemistry, Biology', timing: '7:00 AM - 9:00 AM', teacher_id: 2, teacher_name: 'Rahul Sharma', status: 'active' }
  ],
  students: [
    { id: 1, name: 'Anjali Singh', roll_no: '10A01', parent_name: 'Ramesh Singh', parent_phone: '+919800000001', batch_id: 1, batch_name: 'Class 10 - Morning', address: '123 Main St, Lucknow', student_class: '10', stream: null, board: 'UP Board', subject_fees: [{ subject: 'Maths', fee: 1500 }, { subject: 'Science', fee: 1500 }], total_fee: 3000, status: 'active', joining_date: '2026-04-01' },
    { id: 2, name: 'Rohan Verma', roll_no: '10A02', parent_name: 'Suresh Verma', parent_phone: '+919800000002', batch_id: 1, batch_name: 'Class 10 - Morning', address: '456 Park Lane, Lucknow', student_class: '10', stream: null, board: 'CBSE', subject_fees: [{ subject: 'Maths', fee: 2000 }, { subject: 'Science', fee: 2000 }], total_fee: 4000, status: 'active', joining_date: '2026-04-01' },
    { id: 3, name: 'Priya Gupta', roll_no: '11B01', parent_name: 'Anil Gupta', parent_phone: '+919800000003', batch_id: 2, batch_name: 'Class 11 PCM - Evening', address: '789 Civil Lines, Lucknow', student_class: '11', stream: 'PCM', board: 'CBSE', subject_fees: [{ subject: 'Physics', fee: 2000 }, { subject: 'Chemistry', fee: 2000 }, { subject: 'Maths', fee: 2000 }], total_fee: 6000, status: 'active', joining_date: '2026-04-01' },
    { id: 4, name: 'Amit Yadav', roll_no: '11B02', parent_name: 'Ravi Yadav', parent_phone: '+919800000004', batch_id: 2, batch_name: 'Class 11 PCM - Evening', address: '12 Gomti Nagar, Lucknow', student_class: '11', stream: 'PCM', board: 'UP Board', subject_fees: [{ subject: 'Physics', fee: 1800 }, { subject: 'Chemistry', fee: 1800 }, { subject: 'Maths', fee: 1800 }], total_fee: 5400, status: 'active', joining_date: '2026-04-01' },
    { id: 5, name: 'Sneha Tiwari', roll_no: '12C01', parent_name: 'Prem Tiwari', parent_phone: '+919800000005', batch_id: 3, batch_name: 'Class 12 PCB - Morning', address: '56 Hazratganj, Lucknow', student_class: '12', stream: 'PCB', board: 'CBSE', subject_fees: [{ subject: 'Physics', fee: 2200 }, { subject: 'Chemistry', fee: 2200 }, { subject: 'Biology', fee: 2200 }], total_fee: 6600, status: 'active', joining_date: '2026-04-01' }
  ],
  teachers: [
    { id: 2, name: 'Rahul Sharma', email: 'rahul@apex.com', phone: '+919876543211', role: 'TEACHER', status: 'active' }
  ],
  fees: [
    { id: 1, student_id: 1, student_name: 'Anjali Singh', batch_name: 'Class 10 - Morning', parent_phone: '+919800000001', total_fee: 3000, amount_paid: 1000, status: 'Partial', due_date: '2026-12-01' },
    { id: 2, student_id: 2, student_name: 'Rohan Verma', batch_name: 'Class 10 - Morning', parent_phone: '+919800000002', total_fee: 4000, amount_paid: 4000, status: 'Paid', due_date: '2026-12-01' },
    { id: 3, student_id: 3, student_name: 'Priya Gupta', batch_name: 'Class 11 PCM - Evening', parent_phone: '+919800000003', total_fee: 6000, amount_paid: 0, status: 'Pending', due_date: '2026-12-01' },
    { id: 4, student_id: 4, student_name: 'Amit Yadav', batch_name: 'Class 11 PCM - Evening', parent_phone: '+919800000004', total_fee: 5400, amount_paid: 5400, status: 'Paid', due_date: '2026-12-01' },
    { id: 5, student_id: 5, student_name: 'Sneha Tiwari', batch_name: 'Class 12 PCB - Morning', parent_phone: '+919800000005', total_fee: 6600, amount_paid: 3300, status: 'Partial', due_date: '2026-12-01' }
  ],
  attendance: [],
  payments: [],
  settings: {
    institute_name: 'Apex Coaching Institute',
    institute_phone: '+919876543210',
    institute_address: '123 Education Hub, Lucknow, UP',
    whatsapp_provider: 'mock',
    absent_message_template: 'Dear Parent, your ward {student_name} was absent today from {batch_name}. Please ensure regular attendance. - Apex Institute'
  }
};

function getLocalStore() {
  try {
    const raw = localStorage.getItem('apex_local_store');
    if (raw) return JSON.parse(raw);
  } catch {}
  saveLocalStore(DEFAULT_STORAGE);
  return DEFAULT_STORAGE;
}

function saveLocalStore(data) {
  try {
    localStorage.setItem('apex_local_store', JSON.stringify(data));
  } catch {}
}

function mockApiHandler(endpoint, options = {}) {
  const store = getLocalStore();
  const method = (options.method || 'GET').toUpperCase();
  const [path, queryString] = endpoint.split('?');
  const params = new URLSearchParams(queryString || '');
  const body = options.body ? JSON.parse(options.body) : {};

  // Auth
  if (path === '/auth/login' || path === '/auth/me') {
    return { success: true, data: { user: { id: 1, name: 'Admin', role: 'ADMIN', email: 'admin@apex.com' } } };
  }

  // Dashboard Stats
  if (path === '/dashboard/stats') {
    const active = store.students.filter(s => s.status === 'active');
    const totalFee = store.fees.reduce((a, b) => a + (b.total_fee || 0), 0);
    const collected = store.fees.reduce((a, b) => a + (b.amount_paid || 0), 0);
    return {
      success: true,
      data: {
        total_students: active.length,
        total_batches: store.batches.length,
        present_today: active.length - 1,
        absent_today: 1,
        attendance_percentage: 80,
        total_fees: totalFee,
        fees_collected: collected,
        fees_pending: totalFee - collected
      }
    };
  }

  // Dashboard Batch Summary
  if (path === '/dashboard/batch-summary') {
    const summary = store.batches.map(b => {
      const bStudents = store.students.filter(s => s.batch_id === b.id && s.status === 'active');
      return {
        ...b,
        total_students: bStudents.length,
        present: Math.max(0, bStudents.length - 1),
        absent: Math.min(1, bStudents.length)
      };
    });
    return { success: true, data: summary };
  }

  // Batches
  if (path === '/batches') {
    if (method === 'POST') {
      const newBatch = { id: Date.now(), ...body, status: 'active', teacher_name: 'Rahul Sharma' };
      store.batches.push(newBatch);
      saveLocalStore(store);
      return { success: true, data: newBatch };
    }
    return { success: true, data: store.batches };
  }

  // Students
  if (path === '/students') {
    if (method === 'POST') {
      const newStudent = {
        id: Date.now(),
        ...body,
        status: 'active',
        batch_name: (store.batches.find(b => b.id === Number(body.batch_id)) || {}).name || ''
      };
      store.students.push(newStudent);
      store.fees.push({
        id: Date.now() + 1,
        student_id: newStudent.id,
        student_name: newStudent.name,
        batch_name: newStudent.batch_name,
        parent_phone: newStudent.parent_phone,
        total_fee: newStudent.total_fee || 0,
        amount_paid: 0,
        status: 'Pending',
        due_date: '2026-12-01'
      });
      saveLocalStore(store);
      return { success: true, data: newStudent };
    }
    let list = store.students.filter(s => s.status === 'active');
    const batchId = params.get('batch_id');
    const search = params.get('search');
    if (batchId) list = list.filter(s => String(s.batch_id) === String(batchId));
    if (search) {
      const q = search.toLowerCase();
      list = list.filter(s => s.name.toLowerCase().includes(q) || (s.roll_no && s.roll_no.toLowerCase().includes(q)));
    }
    return { success: true, data: list, total: list.length };
  }

  // Delete student
  if (path.startsWith('/students/') && method === 'DELETE') {
    const id = Number(path.replace('/students/', ''));
    const s = store.students.find(s => s.id === id);
    if (s) s.status = 'inactive';
    saveLocalStore(store);
    return { success: true, message: 'Student removed' };
  }

  // Teachers
  if (path === '/teachers') {
    if (method === 'POST') {
      const newTeacher = { id: Date.now(), ...body, role: 'TEACHER', status: 'active' };
      store.teachers.push(newTeacher);
      saveLocalStore(store);
      return { success: true, data: newTeacher };
    }
    return { success: true, data: store.teachers };
  }

  // Attendance batch roster
  if (path === '/attendance/batch-roster') {
    const bid = Number(params.get('batch_id') || 1);
    const date = params.get('date');
    const students = store.students.filter(s => s.batch_id === bid && s.status === 'active');
    const roster = students.map(s => {
      const att = store.attendance.find(a => a.student_id === s.id && a.date === date);
      return { ...s, attendance_status: att ? att.status : null };
    });
    return { success: true, data: roster };
  }

  // Attendance submit
  if (path === '/attendance/submit') {
    const { batch_id, date, records } = body;
    records.forEach(r => {
      const idx = store.attendance.findIndex(a => a.student_id === r.student_id && a.date === date);
      if (idx >= 0) store.attendance[idx].status = r.status;
      else store.attendance.push({ id: Date.now(), batch_id, date, student_id: r.student_id, status: r.status });
    });
    saveLocalStore(store);
    return { success: true, message: 'Attendance recorded' };
  }

  // Absent list
  if (path === '/attendance/absent-list') {
    const bid = Number(params.get('batch_id') || 1);
    const date = params.get('date');
    const absentIds = store.attendance.filter(a => a.batch_id === bid && a.date === date && a.status === 'A').map(a => a.student_id);
    const list = store.students.filter(s => absentIds.includes(s.id));
    return { success: true, data: list };
  }

  // WhatsApp Absent broadcast
  if (path === '/messages/send-absent-broadcast') {
    return { success: true, data: { sent: 1, message: 'WhatsApp message broadcast sent' } };
  }

  // Fees list
  if (path === '/fees') {
    return { success: true, data: store.fees };
  }

  // Fees summary
  if (path === '/fees/summary') {
    const total = store.fees.reduce((a, b) => a + (b.total_fee || 0), 0);
    const collected = store.fees.reduce((a, b) => a + (b.amount_paid || 0), 0);
    return {
      success: true,
      data: {
        total_fee: total,
        amount_collected: collected,
        amount_pending: total - collected,
        paid_count: store.fees.filter(f => f.status === 'Paid').length,
        partial_count: store.fees.filter(f => f.status === 'Partial').length,
        pending_count: store.fees.filter(f => f.status === 'Pending').length
      }
    };
  }

  // Fees record payment
  if (path === '/fees/record-payment') {
    const { student_id, amount, payment_mode, notes } = body;
    const fee = store.fees.find(f => f.student_id === student_id);
    if (fee) {
      fee.amount_paid = (fee.amount_paid || 0) + Number(amount);
      fee.status = fee.amount_paid >= fee.total_fee ? 'Paid' : 'Partial';
      saveLocalStore(store);
    }
    return { success: true, data: fee };
  }

  // Dashboard Absent Grouped
  if (path === '/dashboard/absent-grouped') {
    return { success: true, data: [] };
  }

  // Fees defaulters
  if (path === '/fees/defaulters') {
    const defaulters = store.fees.filter(f => f.status !== 'Paid');
    return { success: true, data: defaulters };
  }

  // Delete teacher
  if (path.startsWith('/teachers/') && method === 'DELETE') {
    const id = Number(path.replace('/teachers/', ''));
    const t = store.teachers.find(t => t.id === id);
    if (t) t.status = 'inactive';
    saveLocalStore(store);
    return { success: true, message: 'Teacher removed' };
  }

  // Settings
  if (path === '/settings') {
    if (method === 'PUT') {
      store.settings = { ...store.settings, ...body };
      saveLocalStore(store);
      return { success: true, data: store.settings };
    }
    return { success: true, data: store.settings };
  }

  return { success: true, data: [] };
}

export function setToken(token) {
  if (token) localStorage.setItem('apex_token', token);
  else localStorage.removeItem('apex_token');
}

async function request(endpoint, options = {}) {
  try {
    const res = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers: { 'Content-Type': 'application/json', ...(options.headers || {}) }
    });

    if (res.ok) {
      return await res.json();
    }
  } catch (err) {
    // If backend is not available (e.g. Vercel static hosting), fallback seamlessly to mockApiHandler
  }

  return mockApiHandler(endpoint, options);
}

export const api = {
  login: () => Promise.resolve({ success: true, data: { user: { id: 1, name: 'Admin', role: 'ADMIN' } } }),
  getMe: () => Promise.resolve({ success: true, data: { user: { id: 1, name: 'Admin', role: 'ADMIN' } } }),
  getBatches: () => request('/batches'),
  getBatch: (id) => request(`/batches/${id}`),
  createBatch: (data) => request('/batches', { method: 'POST', body: JSON.stringify(data) }),
  updateBatch: (id, data) => request(`/batches/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  getStudents: (params = {}) => {
    const q = new URLSearchParams(params).toString();
    return request(`/students${q ? `?${q}` : ''}`);
  },
  createStudent: (data) => request('/students', { method: 'POST', body: JSON.stringify(data) }),
  updateStudent: (id, data) => request(`/students/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteStudent: (id) => request(`/students/${id}`, { method: 'DELETE' }),
  getTeachers: () => request('/teachers'),
  deleteTeacher: (id) => request(`/teachers/${id}`, { method: 'DELETE' }),
  getDashboardAbsentGrouped: (date) => request(`/dashboard/absent-grouped?date=${date}`),
  getDefaulters: (params = {}) => {
    const q = new URLSearchParams(params).toString();
    return request(`/fees/defaulters${q ? `?${q}` : ''}`);
  },
  getBatchRoster: (batchId, date) => request(`/attendance/batch-roster?batch_id=${batchId}&date=${date}`),
  submitAttendance: (batchId, date, records) => request('/attendance/submit', { method: 'POST', body: JSON.stringify({ batch_id: batchId, date, records }) }),
  getAbsentList: (batchId, date) => request(`/attendance/absent-list?batch_id=${batchId}&date=${date}`),
  sendAbsentBroadcast: (batchId, date) => request('/messages/send-absent-broadcast', { method: 'POST', body: JSON.stringify({ batch_id: batchId, date }) }),
  getDashboardStats: (date) => request(`/dashboard/stats?date=${date}`),
  getDashboardBatchSummary: (date) => request(`/dashboard/batch-summary?date=${date}`),
  getSettings: () => request('/settings'),
  updateSettings: (data) => request('/settings', { method: 'PUT', body: JSON.stringify(data) }),
  getFees: (params = {}) => {
    const q = new URLSearchParams(params).toString();
    return request(`/fees${q ? `?${q}` : ''}`);
  },
  getFeeSummary: () => request('/fees/summary'),
  recordPayment: (data) => request('/fees/record-payment', { method: 'POST', body: JSON.stringify(data) }),
  getReceipt: (receiptNumber) => request(`/fees/receipt/${encodeURIComponent(receiptNumber)}`),
  sendFeeReminderBroadcast: (batchId = null) => request('/fees/send-reminder-broadcast', { method: 'POST', body: JSON.stringify({ batch_id: batchId }) })
};
