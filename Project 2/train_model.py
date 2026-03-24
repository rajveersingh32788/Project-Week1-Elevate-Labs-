"""
Healthcare Appointment No-Show Prediction
Decision Tree Model Training & Evaluation
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import joblib
import warnings
warnings.filterwarnings('ignore')

from sklearn.tree import DecisionTreeClassifier, export_text, plot_tree
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (classification_report, confusion_matrix,
                              roc_auc_score, roc_curve, accuracy_score,
                              precision_score, recall_score, f1_score)
from sklearn.preprocessing import LabelEncoder

# ── Colors ──────────────────────────────────────────────────────────────────
BLUE   = '#1E5799'
RED    = '#C0392B'
GREEN  = '#27AE60'
ORANGE = '#E67E22'
GRAY   = '#95A5A6'
BG     = '#F8FAFC'

plt.rcParams.update({
    'figure.facecolor': BG,
    'axes.facecolor':   BG,
    'font.family':      'DejaVu Sans',
    'axes.spines.top':  False,
    'axes.spines.right':False,
})

# ─────────────────────────────────────────────────────────────────────────────
# 1. LOAD & CLEAN
# ─────────────────────────────────────────────────────────────────────────────
df = pd.read_csv('data/appointments.csv')
df['AppointmentDay']  = pd.to_datetime(df['AppointmentDay'])
df['ScheduledDay']    = pd.to_datetime(df['ScheduledDay'])

# Engineered features
df['WaitDays']        = (df['AppointmentDay'] - df['ScheduledDay']).dt.days.clip(0)
df['IsWeekend']       = df['AppointmentDay'].dt.dayofweek.isin([5, 6]).astype(int)
df['AppointmentMonth']= df['AppointmentDay'].dt.month
df['AgeGroup'] = pd.cut(df['Age'], bins=[0,12,17,35,60,120],
                         labels=['Child','Teen','Young Adult','Adult','Senior'])

le = LabelEncoder()
df['Gender_enc']      = le.fit_transform(df['Gender'])          # F=0, M=1
df['AgeGroup_enc']    = le.fit_transform(df['AgeGroup'].astype(str))
df['Weekday_enc']     = le.fit_transform(df['AppointmentWeekday'])

print("=== Dataset Overview ===")
print(f"Rows: {len(df)}  |  No-show rate: {df['No-show'].mean():.1%}")
print(df[['Age','WaitDays','SMS_received','Scholarship','No-show']].describe().round(2))

# ─────────────────────────────────────────────────────────────────────────────
# 2. FEATURES & SPLIT
# ─────────────────────────────────────────────────────────────────────────────
FEATURES = ['Age','Gender_enc','Scholarship','Hipertension','Diabetes',
            'Alcoholism','Handcap','SMS_received','WaitDays',
            'IsWeekend','AppointmentMonth','AgeGroup_enc','Weekday_enc']

X = df[FEATURES]
y = df['No-show']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2,
                                                      random_state=42,
                                                      stratify=y)
print(f"\nTrain: {len(X_train)}  Test: {len(X_test)}")

# ─────────────────────────────────────────────────────────────────────────────
# 3. TRAIN DECISION TREE
# ─────────────────────────────────────────────────────────────────────────────
dt = DecisionTreeClassifier(max_depth=6, min_samples_split=50,
                             min_samples_leaf=25, class_weight='balanced',
                             random_state=42)
dt.fit(X_train, y_train)

y_pred  = dt.predict(X_test)
y_proba = dt.predict_proba(X_test)[:, 1]

acc  = accuracy_score(y_test, y_pred)
prec = precision_score(y_test, y_pred)
rec  = recall_score(y_test, y_pred)
f1   = f1_score(y_test, y_pred)
auc  = roc_auc_score(y_test, y_proba)
cv   = cross_val_score(dt, X, y, cv=5, scoring='roc_auc').mean()

print(f"\n=== Model Performance ===")
print(f"Accuracy : {acc:.3f}")
print(f"Precision: {prec:.3f}")
print(f"Recall   : {rec:.3f}")
print(f"F1 Score : {f1:.3f}")
print(f"AUC-ROC  : {auc:.3f}")
print(f"CV AUC   : {cv:.3f}")
print("\n", classification_report(y_test, y_pred, target_names=['Show','No-Show']))

# Save model
joblib.dump(dt, 'models/noshow_decision_tree.pkl')
print("Model saved → models/noshow_decision_tree.pkl")

# Save metrics
metrics = dict(Accuracy=acc, Precision=prec, Recall=rec, F1=f1, AUC_ROC=auc, CV_AUC=cv)
pd.DataFrame([metrics]).to_csv('models/model_metrics.csv', index=False)

# ─────────────────────────────────────────────────────────────────────────────
# 4. FEATURE IMPORTANCE
# ─────────────────────────────────────────────────────────────────────────────
fi = pd.DataFrame({'Feature': FEATURES, 'Importance': dt.feature_importances_})
fi = fi.sort_values('Importance', ascending=False)
fi.to_csv('models/feature_importance.csv', index=False)

# ─────────────────────────────────────────────────────────────────────────────
# 5. TREND ANALYSIS EXPORT
# ─────────────────────────────────────────────────────────────────────────────
# SMS analysis
sms = df.groupby('SMS_received')['No-show'].mean().reset_index()
sms.columns = ['SMS_received','NoShow_Rate']
sms.to_csv('models/sms_noshow.csv', index=False)

# Age group analysis
age = df.groupby('AgeGroup', observed=True)['No-show'].mean().reset_index()
age.columns = ['AgeGroup','NoShow_Rate']
age.to_csv('models/age_noshow.csv', index=False)

# Weekday analysis
wd = df.groupby('AppointmentWeekday')['No-show'].mean().reset_index()
wd.columns = ['Weekday','NoShow_Rate']
wd.to_csv('models/weekday_noshow.csv', index=False)

# Neighbourhood analysis
nb = df.groupby('Neighbourhood')['No-show'].agg(['mean','count']).reset_index()
nb.columns = ['Neighbourhood','NoShow_Rate','Total_Appointments']
nb.to_csv('models/neighbourhood_noshow.csv', index=False)

# Predictions export
X_test_out = X_test.copy()
X_test_out['Actual']        = y_test.values
X_test_out['Predicted']     = y_pred
X_test_out['NoShow_Prob']   = y_proba.round(3)
X_test_out.to_csv('models/test_predictions.csv', index=False)

# Full dataset with risk scores
df['NoShow_Prob'] = dt.predict_proba(X[FEATURES])[:,1].round(3)
df['Risk_Level']  = pd.cut(df['NoShow_Prob'], bins=[0,.3,.6,1.0],
                            labels=['Low','Medium','High'])
df.to_csv('models/full_predictions.csv', index=False)

print("\n✓ All analysis files exported to models/")

# ─────────────────────────────────────────────────────────────────────────────
# 6. VISUALIZATIONS
# ─────────────────────────────────────────────────────────────────────────────

# Fig 1 – Decision Tree (top 4 levels)
fig, ax = plt.subplots(figsize=(22, 10), facecolor=BG)
plot_tree(dt, max_depth=4, feature_names=FEATURES,
          class_names=['Show','No-Show'], filled=True,
          impurity=False, rounded=True, fontsize=8, ax=ax)
ax.set_title('Decision Tree – Top 4 Levels', fontsize=16, fontweight='bold',
             color=BLUE, pad=15)
plt.tight_layout()
plt.savefig('outputs/decision_tree.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved: decision_tree.png")

# Fig 2 – Feature Importance
fig, ax = plt.subplots(figsize=(10, 6), facecolor=BG)
colors = [BLUE if i < 5 else GRAY for i in range(len(fi))]
bars = ax.barh(fi['Feature'], fi['Importance'], color=colors, edgecolor='white',
               linewidth=0.5, height=0.65)
ax.set_xlabel('Importance Score', fontsize=11)
ax.set_title('Feature Importance – Decision Tree', fontsize=14,
             fontweight='bold', color=BLUE)
ax.axvline(fi['Importance'].mean(), color=RED, linestyle='--', alpha=0.7,
           label=f"Mean ({fi['Importance'].mean():.3f})")
ax.legend(fontsize=9)
for bar, val in zip(bars, fi['Importance']):
    ax.text(bar.get_width() + 0.001, bar.get_y() + bar.get_height()/2,
            f'{val:.3f}', va='center', fontsize=8)
plt.tight_layout()
plt.savefig('outputs/feature_importance.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved: feature_importance.png")

# Fig 3 – ROC Curve
fpr, tpr, _ = roc_curve(y_test, y_proba)
fig, ax = plt.subplots(figsize=(7, 6), facecolor=BG)
ax.plot(fpr, tpr, color=BLUE, lw=2.5, label=f'Decision Tree (AUC = {auc:.3f})')
ax.plot([0,1],[0,1], color=GRAY, linestyle='--', lw=1.5, label='Random Classifier')
ax.fill_between(fpr, tpr, alpha=0.08, color=BLUE)
ax.set_xlabel('False Positive Rate', fontsize=11)
ax.set_ylabel('True Positive Rate', fontsize=11)
ax.set_title('ROC Curve – No-Show Prediction', fontsize=14,
             fontweight='bold', color=BLUE)
ax.legend(fontsize=10)
plt.tight_layout()
plt.savefig('outputs/roc_curve.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved: roc_curve.png")

# Fig 4 – Confusion Matrix
cm = confusion_matrix(y_test, y_pred)
fig, ax = plt.subplots(figsize=(6, 5), facecolor=BG)
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax,
            xticklabels=['Show','No-Show'], yticklabels=['Show','No-Show'],
            linewidths=0.5, linecolor='white')
ax.set_xlabel('Predicted', fontsize=11)
ax.set_ylabel('Actual', fontsize=11)
ax.set_title('Confusion Matrix', fontsize=14, fontweight='bold', color=BLUE)
plt.tight_layout()
plt.savefig('outputs/confusion_matrix.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved: confusion_matrix.png")

# Fig 5 – No-Show by SMS + Age Group (2 panels)
fig, axes = plt.subplots(1, 2, figsize=(13, 5), facecolor=BG)

ax = axes[0]
sms_labels = ['No SMS', 'SMS Sent']
sms_vals   = df.groupby('SMS_received')['No-show'].mean().values * 100
bars = ax.bar(sms_labels, sms_vals, color=[RED, GREEN], width=0.5,
              edgecolor='white', linewidth=1.5)
for bar, val in zip(bars, sms_vals):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
            f'{val:.1f}%', ha='center', fontsize=12, fontweight='bold')
ax.set_ylabel('No-Show Rate (%)', fontsize=11)
ax.set_title('No-Show Rate by SMS Reminder', fontsize=13, fontweight='bold', color=BLUE)
ax.set_ylim(0, sms_vals.max() * 1.25)

ax = axes[1]
age_data = df.groupby('AgeGroup', observed=True)['No-show'].mean() * 100
order = ['Child','Teen','Young Adult','Adult','Senior']
age_vals = [age_data.get(g, 0) for g in order]
bars = ax.bar(order, age_vals, color=BLUE, alpha=0.85, edgecolor='white',
              linewidth=1.5)
for bar, val in zip(bars, age_vals):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
            f'{val:.1f}%', ha='center', fontsize=10, fontweight='bold')
ax.set_ylabel('No-Show Rate (%)', fontsize=11)
ax.set_title('No-Show Rate by Age Group', fontsize=13, fontweight='bold', color=BLUE)
ax.set_ylim(0, max(age_vals) * 1.25)
ax.tick_params(axis='x', labelsize=9)

plt.suptitle('Patient No-Show Trends', fontsize=15, fontweight='bold',
             color=BLUE, y=1.02)
plt.tight_layout()
plt.savefig('outputs/noshow_trends.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved: noshow_trends.png")

# Fig 6 – No-Show by Weekday
fig, ax = plt.subplots(figsize=(9, 5), facecolor=BG)
weekday_order = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
wd_data = df.groupby('AppointmentWeekday')['No-show'].mean() * 100
wd_vals = [wd_data.get(d, 0) for d in weekday_order]
bar_colors = [RED if v == max(wd_vals) else BLUE for v in wd_vals]
bars = ax.bar(weekday_order, wd_vals, color=bar_colors, edgecolor='white', linewidth=1.5)
for bar, val in zip(bars, wd_vals):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
            f'{val:.1f}%', ha='center', fontsize=10, fontweight='bold')
ax.set_ylabel('No-Show Rate (%)', fontsize=11)
ax.set_title('No-Show Rate by Appointment Weekday', fontsize=14,
             fontweight='bold', color=BLUE)
ax.set_ylim(0, max(wd_vals) * 1.25)
red_patch = mpatches.Patch(color=RED, label='Highest day')
ax.legend(handles=[red_patch], fontsize=9)
plt.tight_layout()
plt.savefig('outputs/noshow_weekday.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved: noshow_weekday.png")

# Fig 7 – Risk Distribution
fig, ax = plt.subplots(figsize=(9, 5), facecolor=BG)
ax.hist(df['NoShow_Prob'], bins=40, color=BLUE, edgecolor='white',
        linewidth=0.5, alpha=0.85)
ax.axvline(0.30, color=ORANGE, linestyle='--', lw=2, label='Low/Medium (0.30)')
ax.axvline(0.60, color=RED,    linestyle='--', lw=2, label='Medium/High (0.60)')
ax.set_xlabel('Predicted No-Show Probability', fontsize=11)
ax.set_ylabel('Number of Patients', fontsize=11)
ax.set_title('Risk Score Distribution', fontsize=14, fontweight='bold', color=BLUE)
ax.legend(fontsize=10)
plt.tight_layout()
plt.savefig('outputs/risk_distribution.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved: risk_distribution.png")

# Fig 8 – Model Metrics Summary
fig, ax = plt.subplots(figsize=(9, 5), facecolor=BG)
metric_names = ['Accuracy','Precision','Recall','F1 Score','AUC-ROC']
metric_vals  = [acc, prec, rec, f1, auc]
bar_colors   = [GREEN if v >= 0.70 else ORANGE if v >= 0.55 else RED for v in metric_vals]
bars = ax.bar(metric_names, metric_vals, color=bar_colors, edgecolor='white',
              linewidth=1.5, width=0.55)
for bar, val in zip(bars, metric_vals):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005,
            f'{val:.3f}', ha='center', fontsize=12, fontweight='bold')
ax.axhline(0.70, color=GRAY, linestyle='--', lw=1.5, label='0.70 benchmark')
ax.set_ylim(0, 1.1)
ax.set_ylabel('Score', fontsize=11)
ax.set_title('Model Performance Metrics', fontsize=14, fontweight='bold', color=BLUE)
ax.legend(fontsize=9)
plt.tight_layout()
plt.savefig('outputs/model_metrics.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved: model_metrics.png")

print("\n✓ All 8 visualizations saved to outputs/")
print(f"\n{'='*50}")
print("SUMMARY")
print(f"{'='*50}")
print(f"Dataset       : 5,000 appointments")
print(f"No-Show Rate  : {df['No-show'].mean():.1%}")
print(f"Model AUC-ROC : {auc:.3f}")
print(f"Model Accuracy: {acc:.3f}")
risk_dist = df['Risk_Level'].value_counts()
print(f"\nRisk Distribution:")
for lvl in ['High','Medium','Low']:
    print(f"  {lvl:8s}: {risk_dist.get(lvl,0):5d} patients")
