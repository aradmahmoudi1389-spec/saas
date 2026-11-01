window.BRANDYAR_IDENTITY={
  storageKey:'brandyar-identity-v3',
  legacyKeys:['brandyar-identity-v2'],
  migrated:'brandyar-identity-migrated',
  sections:[
    {id:'work',title:'دربارهٔ کار تو',fields:[
      ['professionalRole','نقش یا عنوان حرفه‌ای','text','مثلاً مشاور کسب‌وکار یا طراح'],
      ['industry','حوزهٔ کاری','text','در چه حوزه‌ای فعالیت می‌کنی؟'],
      ['experience','تجربه','textarea','چه تجربه‌ای داری؟ این بخش اختیاری است.'],
      ['skills','مهارت‌های اصلی','list','هر مهارت را با ویرگول جدا کن.'],
      ['services','خدمات یا کارهایی که ارائه می‌کنی','list','هر خدمت را با ویرگول جدا کن.']
    ]},
    {id:'audience',title:'دربارهٔ مخاطب تو',fields:[
      ['targetDescription','مخاطب اصلی','textarea','به چه کسانی کمک می‌کنی؟'],
      ['primaryGroup','گروهی که بیشتر می‌خواهی به آن‌ها کمک کنی','text','مثلاً صاحبان کسب‌وکارهای کوچک'],
      ['needs','نیازهای مخاطب','list','نیازها را با ویرگول جدا کن.'],
      ['problems','مسئله‌هایی که مخاطب با آن‌ها روبه‌روست','list','مسئله‌ها را با ویرگول جدا کن.']
    ]},
    {id:'value',title:'ارزشی که ایجاد می‌کنی',fields:[
      ['valueProposition','ارزش پیشنهادی','textarea','چه نتیجه یا کمکی ارائه می‌دهی؟'],
      ['differentiators','تفاوت حرفه‌ای و رویکرد خاص','list','هر مورد را با ویرگول جدا کن.']
    ]},
    {id:'direction',title:'مسیر حرفه‌ای تو',fields:[
      ['professionalGoals','هدف حرفه‌ای','list','هدف‌ها را با ویرگول جدا کن.'],
      ['desiredPerception','تصویری که می‌خواهی در ذهن مخاطب بسازی','textarea','دوست داری با چه ویژگی‌ای شناخته شوی؟'],
      ['personalValues','ارزش‌های شخصی یا حرفه‌ای','list','ارزش‌ها را با ویرگول جدا کن.'],
      ['preferredTopics','موضوع‌هایی که می‌خواهی دربارهٔ آن‌ها صحبت کنی','list','موضوع‌ها را با ویرگول جدا کن.'],
      ['excludedTopics','موضوع‌هایی که نمی‌خواهی دربارهٔ آن‌ها صحبت کنی','list','موضوع‌های خارج از تمرکز را بنویس.']
    ]}
  ],
  required:['professionalRole','industry','targetDescription','problems','valueProposition','professionalGoals'],
  lists:['skills','services','differentiators','professionalGoals','personalValues','preferredTopics','excludedTopics'],
  texts:['professionalRole','industry','experience','valueProposition','desiredPerception','targetDescription','primaryGroup'],
  state:{identity:null,access:null,testCompleted:false,trialUsed:false,csrf:'',signedIn:false,demoAuth:true,error:'',loadFailed:false,saving:false},
  empty(){return {id:'brand-identity',status:'not_started',completionPercentage:0,professionalRole:'',industry:'',experience:'',skills:[],services:[],targetAudience:{description:'',primaryGroup:'',needs:[],problems:[]},valueProposition:'',differentiators:[],professionalGoals:[],personalValues:[],preferredTopics:[],excludedTopics:[],desiredPerception:'',testInsight:{exists:false,summary:'',isApprovedForBrandUse:false,source:''},approvedSections:[],draftSections:[],createdAt:null,updatedAt:null,approvedAt:null}},
  normalizeList(value){return [...new Set((Array.isArray(value)?value:String(value||'').split(/[،,\n]/)).map(x=>String(x).trim()).filter(Boolean).map(x=>x.slice(0,160)))].slice(0,20)},
  normalize(value){const base=this.empty(),v={...base,...(value||{}),targetAudience:{...base.targetAudience,...((value||{}).targetAudience||{})},testInsight:{...base.testInsight,...((value||{}).testInsight||{})},approvedSections:Array.isArray(value?.approvedSections)?value.approvedSections:[],draftSections:Array.isArray(value?.draftSections)?value.draftSections:[]};for(const key of this.lists)v[key]=this.normalizeList(v[key]);for(const key of ['needs','problems'])v.targetAudience[key]=this.normalizeList(v.targetAudience[key]);for(const key of this.texts){const nested=key==='targetDescription'?'description':key==='primaryGroup'?'primaryGroup':null;if(nested)v.targetAudience[nested]=String(v.targetAudience[nested]||'').trim().slice(0,2000);else v[key]=String(v[key]||'').trim().slice(0,2000)}return v},
  current(){return this.normalize(this.state.identity)},
  value(v,key){if(key==='targetDescription')return v.targetAudience.description;if(key==='primaryGroup')return v.targetAudience.primaryGroup;if(key==='needs'||key==='problems')return v.targetAudience[key];return v[key]},
  has(v,key){const x=this.value(v,key);return Array.isArray(x)?x.length>0:Boolean(x)},
  missing(v){return this.required.filter(key=>!this.has(v,key))},
  sectionComplete(v,section){return section.fields.map(([key])=>key).filter(key=>this.required.includes(key)).every(key=>this.has(v,key))},
  draftPointers(value){const current=this.current(),payload=this.normalize({...current,...value,targetAudience:{...current.targetAudience,...(value.targetAudience||{})}}),out={};for(const key of this.lists)out[key]=payload[key];for(const key of ['needs','problems'])out[key]=payload.targetAudience[key];for(const key of this.texts)out[key]=key==='targetDescription'?payload.targetAudience.description:key==='primaryGroup'?payload.targetAudience.primaryGroup:payload[key];return out},
  async refresh(){
    this.state.error='';this.state.loadFailed=false;
    try{
      const res=await fetch('/api/brandyar',{credentials:'same-origin',cache:'no-store'});
      const data=await res.json();
      if(!res.ok)throw new Error(data.error||'load');
      this.state.signedIn=Boolean(data.data?.signedIn);
      this.state.csrf=data.data?.csrf||'';
      this.state.identity=data.data?.identity||null;
      this.state.access=data.data?.access||{status:'none',planId:'',planName:'',simulation:true};
      this.state.testCompleted=Boolean(data.data?.testCompleted);
      this.state.trialUsed=Boolean(data.data?.trialUsed);
      this.state.demoAuth=data.data?.demoAuth!==false;
      await this.migrateLegacy();
      return this.state;
    }catch(error){
      this.dropSession();
      this.state.loadFailed=true;
      this.state.error='بازیابی اطلاعات انجام نشد؛ دوباره تلاش کن یا از مسیر تست وارد شو.';
      throw error;
    }
  },
  dropSession(){this.state.signedIn=false;this.state.csrf='';this.state.identity=null;this.state.access=null;this.state.testCompleted=false;this.state.trialUsed=false},
  async migrateLegacy(){
    if(this.state.loadFailed||!this.state.signedIn)return;
    try{if(localStorage.getItem(this.migrated)==='1')return}catch{return}
    let legacy=null;try{for(const key of this.legacyKeys){const raw=localStorage.getItem(key);if(raw){legacy=JSON.parse(raw);break}}}catch{}
    try{
      if(legacy&&legacy.professionalRole!==undefined&&!this.current().professionalRole){
        await this.save(this.draftPointers(legacy));
      }
      localStorage.setItem(this.migrated,'1');
    }catch{}
  },
  // sections: the part keys the user just edited; the server un-approves only these and fails the save when approval is stale.
  async save(value,insightApproval,sections){
    const current=this.current();
    const payload={...this.draftPointers(current),...this.draftPointers(value||{})};
    if(value?.targetAudience)payload.targetAudience={...current.targetAudience,...value.targetAudience};
    return this.post({action:'identity_save',identity:payload,sections:Array.isArray(sections)&&sections.length?sections:undefined,...(insightApproval===undefined?{}:{insightApproval})});
  },
  async approve(approvedAt){return this.post({action:'identity_approve',approvedAt:approvedAt||null})},
  async grant(planId){return this.post({action:'trial_grant',planId})},
  async post(body){this.state.saving=true;try{const res=await fetch('/api/brandyar',{method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/json'},body:JSON.stringify({...body,csrf:this.state.csrf})});const data=await res.json();if(res.status===401)this.dropSession();if(!res.ok){const error=new Error(data.error||'save');error.status=res.status;throw error}if(data.data.identity)this.state.identity=data.data.identity;if(data.data.access)this.state.access=data.data.access;this.state.error='';return data.data}catch(error){if(!error.status)error.message='ارتباط برقرار نشد؛ دوباره تلاش کن.';throw error}finally{this.state.saving=false}},
  accessLabel(access){if(!access)return 'نامشخص';return {trial:'دسترسی آزمایشی فعال',active:'دسترسی فعال',expired:'دسترسی پایان یافته',suspended:'دسترسی غیرفعال'}[access.status]||'بدون دسترسی فعال'},
  accessKey(access){return ['trial','active','expired','suspended'].includes(access?.status)?access.status:'none'},
  accessState(){
    if(this.state.loadFailed&&!this.state.signedIn)return 'error';
    if(!this.state.signedIn)return 'signed_out';
    const key=this.accessKey(this.state.access);
    if(key==='trial'||key==='active')return 'active';
    if(key==='expired'||key==='suspended')return 'ended';
    return this.state.testCompleted?'completed_no_access':'no_test';
  },
  accessCopy(){
    const access=this.state.access;
    switch(this.accessState()){
      case 'error':return {label:'وضعیت نامشخص',title:'وضعیت دسترسی خوانده نشد',text:'برای دیدن وضعیت دسترسی، دوباره تلاش کن.',action:'تلاش دوباره',plan:''};
      case 'signed_out':return {label:'بدون نشست',title:'حساب کاربری در دسترس نیست',text:'این بخش فقط برای کاربر واردشده نمایش داده می‌شود.',action:'شروع یا ادامهٔ تست',plan:''};
      case 'no_test':return {label:'تست کامل نشده',title:'تست پرسونال برند هنوز کامل نشده',text:'تست مقدمهٔ مسیر است. تا وقتی کامل نشود، پیشنهاد برندیـار نمایش داده نمی‌شود.',action:'رفتن به تست',plan:''};
      case 'completed_no_access':return {label:'تکمیل تست · بدون ورود',title:'تست تکمیل شده، ورود به برندیـار انجام نشده',text:'می‌توانی تعرفه‌ها را ببینی و اگر خواستی فعال‌سازی آزمایشی را بررسی کنی.',action:this.state.trialUsed?'تلاش دوباره برای فعال‌سازی':'مشاهدهٔ تعرفه‌ها',plan:''};
      case 'active':return {label:access.status==='trial'?'دسترسی آزمایشی':'دسترسی فعال',title:access.status==='trial'?'دسترسی آزمایشی برندیـار فعال است':'دسترسی برندیـار فعال است',text:access.status==='trial'?'این دسترسی آزمایشی است و پرداخت واقعی انجام نشده است.':'دسترسی فعال است و می‌توانی وارد پنل شوی.',action:'ورود به پنل برندیـار',plan:access.planName||''};
      default:return {label:'دسترسی پایان یافته',title:access.status==='suspended'?'دسترسی برندیـار غیرفعال است':'دسترسی برندیـار پایان یافته',text:'محصول در حال حاضر برای حساب تو فعال نیست. اطلاعات هویت و خروجی‌های قبلی تا مشخص‌شدن وضعیت نمایش داده نمی‌شوند.',action:'مشاهدهٔ تعرفه‌ها و فعال‌سازی',plan:access.planName||''};
    }
  },
  statusLabel(status){return {not_started:'شروع نشده',in_progress:'در حال تکمیل',ready_for_review:'آمادهٔ مرور',approved:'تأییدشده توسط شما',needs_revision:'نیازمند بازبینی'}[status]||'شروع نشده'}
};