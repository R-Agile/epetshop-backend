import express from "express";
import mongoose from "mongoose";
import bcrypt from "bcryptjs";
import jwt from "jsonwebtoken";
import cors from "cors";
import cookieParser from "cookie-parser";
import dotenv from "dotenv";

dotenv.config();

const app = express();

// ================== CONFIG ==================
const PORT = process.env.PORT || 5000;
const JWT_SECRET = process.env.JWT_SECRET;
const MONGODB_URI = process.env.MONGODB_URI;
g

// ================== MIDDLEWARE ==================
app.use(cors({  
  origin: true,
  credentials: true
}));
app.use(express.json());
app.use(cookieParser());

// ================== DB ==================
mongoose.connect(MONGODB_URI)
  .then(() => console.log("✅ MongoDB connected successfully"))
  .catch(err => console.error("❌ MongoDB connection error:", err));

// ================== MODELS ==================



const userSchema = new mongoose.Schema({
  name: { type: String, required: true },
  email: { type: String, required: true, unique: true },
  password: { type: String, required: true }
}, { timestamps: true });

const User = mongoose.model("User", userSchema);

// ================== TOKEN BLACKLIST ==================
const tokenBlacklist = new Set();

// ================== ROUTES ==================

// Health check
app.get("/api/health", (req, res) => {
  res.json({ 
    success: true, 
    message: "Server is running",
    mongodb: mongoose.connection.readyState === 1 ? "connected" : "disconnected"
  });
});

// LOGIN
app.post("/api/login", async (req, res) => {
  try {
    const { email, password } = req.body;
    
    if (!email || !password) {
      return res.status(400).json({
        success: false,
        error: "Email and password are required"
      });
    }
    
    const user = await User.findOne({ email });
    
    if (!user) {
      return res.status(401).json({
        success: false,
        error: "Invalid credentials"
      });
    }
    
    const isMatch = await bcrypt.compare(password, user.password);
    
    if (!isMatch) {
      return res.status(401).json({
        success: false,
        error: "Invalid credentials"
      });
    }
    
    const token = jwt.sign(
      { userId: user._id },
      JWT_SECRET,
      { expiresIn: "1h" }
    );
    
    res.cookie('authToken', token, {
      httpOnly: true,
      secure: false,
      sameSite: 'lax',
      maxAge: 3600000
    });
    
    res.status(200).json({
      success: true,
      user: {
        id: user._id,
        name: user.name,
        email: user.email
      },
      token,
      message: "Login successful"
    });
  } catch (error) {
    console.error("Login error:", error);
    res.status(500).json({
      success: false,
      error: "Server error during login"
    });
  }
});

// ================== AUTH MIDDLEWARE ==================
const authMiddleware = (req, res, next) => {
  let token = req.cookies.authToken;
  
  if (!token) {
    const authHeader = req.headers.authorization;
    if (authHeader && authHeader.startsWith('Bearer ')) {
      token = authHeader.split(" ")[1];
    }
  }
  
  if (!token) {
    return res.status(401).json({ 
      success: false,
      error: "Authentication required"
    });
  }
  
  if (tokenBlacklist.has(token)) {
    return res.status(401).json({ 
      success: false,
      error: "Token invalidated"
    });
  }
  
  try {
    req.user = jwt.verify(token, JWT_SECRET);
    req.token = token;
    next();
  } catch (error) {
    return res.status(401).json({ 
      success: false,
      error: "Invalid or expired token"
    });
  }
};

// VERIFY AUTH
app.get("/api/verify", authMiddleware, (req, res) => {
  res.status(200).json({
    success: true,
    authenticated: true,
    userId: req.user.userId
  });
});

// LOGOUT
app.post("/api/logout", authMiddleware, (req, res) => {
  const token = req.token;
  tokenBlacklist.add(token);
  
  res.clearCookie('authToken', {
    httpOnly: true,
    secure: false,
    sameSite: 'lax'
  });
  
  res.status(200).json({ 
    success: true, 
    message: "Logged out successfully" 
  });
});

// PROFILE
app.get("/api/profile", authMiddleware, async (req, res) => {
  try {
    const user = await User.findById(req.user.userId).select('-password');
    
    if (!user) {
      return res.status(404).json({
        success: false,
        error: "User not found"
      });
    }
    
    res.status(200).json({
      success: true,
      user: {
        id: user._id,
        name: user.name,
        email: user.email
      }
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: "Server error"
    });
  }
});

// ================== ERROR HANDLER ==================
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ 
    success: false,
    error: "Internal server error"
  });
});

// ================== SERVER ==================
app.listen(PORT, () => {
  console.log(`🚀 Server running on http://localhost:${PORT}`);
  console.log(`📊 Health check: http://localhost:${PORT}/api/health`);
});